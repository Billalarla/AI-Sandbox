"""
CVR API Client for fetching Danish company data
Integrates with cvrapi.dk to get company information for lead scoring
"""
import requests
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict
from django.conf import settings
from django.core.cache import cache


logger = logging.getLogger(__name__)


@dataclass
class CVRCompanyData:
    """Data structure for CVR company information"""
    cvr_number: str
    company_name: str
    industry_code: str
    industry_text: str
    employee_count: int
    annual_revenue: Optional[float]
    address: str
    city: str
    postal_code: str
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]
    status: str  # 'active', 'inactive', etc.
    established_date: Optional[str]
    legal_form: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class CVRAPIError(Exception):
    """Custom exception for CVR API errors"""
    pass


class CVRAPIClient:
    """
    Client for interacting with cvrapi.dk
    
    Note: You need to register at https://cvrapi.dk/ to get an API key
    Set CVR_API_KEY in your Django settings
    """
    
    BASE_URL = "https://cvrapi.dk/api"
    CACHE_TTL = 86400  # 24 hours
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'CVR_API_KEY', None)
        if not self.api_key:
            logger.warning("CVR_API_KEY not set in settings. CVR lookups will be limited.")
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CRM-LeadScoring/1.0',
            'Accept': 'application/json'
        })
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request to CVR API"""
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Add API key if available
        if self.api_key:
            params['token'] = self.api_key
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if 'error' in data:
                raise CVRAPIError(f"CVR API Error: {data.get('error', 'Unknown error')}")
            
            return data
            
        except requests.RequestException as e:
            logger.error(f"CVR API request failed: {e}")
            raise CVRAPIError(f"Failed to fetch data from CVR API: {e}")
        except ValueError as e:
            logger.error(f"Invalid JSON response from CVR API: {e}")
            raise CVRAPIError("Invalid response format from CVR API")
    
    def lookup_by_cvr(self, cvr_number: str) -> Optional[CVRCompanyData]:
        """
        Look up company by CVR number
        
        Args:
            cvr_number: 8-digit CVR number
            
        Returns:
            CVRCompanyData object or None if not found
        """
        # Clean CVR number
        cvr_clean = ''.join(filter(str.isdigit, cvr_number))
        if len(cvr_clean) != 8:
            logger.warning(f"Invalid CVR number format: {cvr_number}")
            return None
        
        # Check cache first
        cache_key = f"cvr_data_{cvr_clean}"
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Using cached CVR data for {cvr_clean}")
            return CVRCompanyData(**cached_data)
        
        try:
            logger.info(f"Fetching CVR data for {cvr_clean}")
            data = self._make_request('', {'vat': cvr_clean, 'format': 'json'})
            
            if not data or 'name' not in data:
                logger.warning(f"No company data found for CVR {cvr_clean}")
                return None
            
            # Parse the response
            company_data = self._parse_cvr_response(data, cvr_clean)
            
            # Cache the result
            cache.set(cache_key, company_data.to_dict(), self.CACHE_TTL)
            
            return company_data
            
        except CVRAPIError as e:
            logger.error(f"Failed to lookup CVR {cvr_clean}: {e}")
            return None
    
    def search_by_name(self, company_name: str, limit: int = 10) -> list[CVRCompanyData]:
        """
        Search companies by name
        
        Args:
            company_name: Company name to search for
            limit: Maximum number of results
            
        Returns:
            List of CVRCompanyData objects
        """
        try:
            logger.info(f"Searching companies by name: {company_name}")
            data = self._make_request('search', {
                'search': company_name,
                'limit': limit,
                'format': 'json'
            })
            
            results = []
            companies = data.get('hits', [])
            
            for company in companies:
                if 'vat' in company:
                    # Get full data for each company
                    full_data = self.lookup_by_cvr(company['vat'])
                    if full_data:
                        results.append(full_data)
            
            return results
            
        except CVRAPIError as e:
            logger.error(f"Failed to search companies by name {company_name}: {e}")
            return []
    
    def _parse_cvr_response(self, data: Dict[str, Any], cvr_number: str) -> CVRCompanyData:
        """Parse CVR API response into CVRCompanyData object"""
        
        # Extract employee count from various possible fields
        employee_count = 0
        if 'employees' in data:
            employee_count = data['employees']
        elif 'employment' in data and isinstance(data['employment'], dict):
            employee_count = data['employment'].get('numEmployees', 0)
        
        # Extract address information
        address_parts = []
        address_data = data.get('address', {})
        if isinstance(address_data, dict):
            street = address_data.get('street', '')
            house_number = address_data.get('streetcode', '')
            if street:
                address_parts.append(street)
            if house_number:
                address_parts.append(str(house_number))
        
        address = ' '.join(address_parts) if address_parts else data.get('address', '')
        city = address_data.get('city', '') if isinstance(address_data, dict) else data.get('city', '')
        postal_code = address_data.get('zipcode', '') if isinstance(address_data, dict) else data.get('zipcode', '')
        
        # Extract industry information
        industry_code = ''
        industry_text = ''
        if 'industrycode' in data:
            industry_code = str(data['industrycode'])
        if 'industrydesc' in data:
            industry_text = data['industrydesc']
        
        # Extract contact information
        phone = data.get('phone', '')
        email = data.get('email', '')
        website = data.get('homepage', '')
        
        # Extract other fields
        status = data.get('status', 'unknown')
        established_date = data.get('startdate', '')
        legal_form = data.get('companyform', '')
        
        # Try to extract annual revenue (might not always be available)
        annual_revenue = None
        if 'revenue' in data:
            try:
                annual_revenue = float(data['revenue'])
            except (ValueError, TypeError):
                pass
        
        return CVRCompanyData(
            cvr_number=cvr_number,
            company_name=data.get('name', ''),
            industry_code=industry_code,
            industry_text=industry_text,
            employee_count=employee_count,
            annual_revenue=annual_revenue,
            address=address,
            city=city,
            postal_code=postal_code,
            phone=phone,
            email=email,
            website=website,
            status=status,
            established_date=established_date,
            legal_form=legal_form
        )
    
    def get_api_usage(self) -> Dict[str, Any]:
        """Get API usage statistics (if supported by the API)"""
        try:
            data = self._make_request('usage', {})
            return data
        except CVRAPIError:
            return {}


# Singleton instance
cvr_client = CVRAPIClient()
