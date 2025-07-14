"""
Lead Scoring Service using CVR API data and ICP criteria
"""
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from django.utils import timezone
from decimal import Decimal

from ..models import Lead
from .cvr_client import cvr_client, CVRCompanyData, CVRAPIError


logger = logging.getLogger(__name__)


@dataclass
class ICPCriteria:
    """Ideal Customer Profile criteria configuration"""
    min_employees: int = 200
    target_industries: List[str] = None
    target_cities: List[str] = None
    target_employee_levels: List[str] = None
    
    def __post_init__(self):
        if self.target_industries is None:
            self.target_industries = ['FMCG', 'Retail', 'SaaS', 'Software', 'Technology']
        if self.target_cities is None:
            self.target_cities = ['Copenhagen', 'København', 'Aarhus', 'Århus']
        if self.target_employee_levels is None:
            self.target_employee_levels = [
                'Manager', 'Senior Manager', 'Director', 'Senior Director',
                'VP', 'Vice President', 'CEO', 'CTO', 'CFO', 'COO',
                'Head of', 'Chief', 'Executive', 'Principal'
            ]


@dataclass
class LeadScoreBreakdown:
    """Detailed breakdown of lead scoring"""
    company_size_score: int
    industry_score: int
    employee_level_score: int
    location_score: int
    total_score: int
    company_size_match: bool
    industry_match: bool
    employee_level_match: bool
    location_match: bool
    max_possible_score: int = 12
    min_possible_score: int = 4
    cvr_data: Optional[CVRCompanyData] = None
    scoring_timestamp: datetime = None
    
    def __post_init__(self):
        if self.scoring_timestamp is None:
            self.scoring_timestamp = timezone.now()
    
    def get_score_percentage(self) -> float:
        """Get score as percentage of max possible"""
        score_range = self.max_possible_score - self.min_possible_score
        adjusted_score = self.total_score - self.min_possible_score
        return (adjusted_score / score_range) * 100 if score_range > 0 else 0
    
    def get_score_grade(self) -> str:
        """Get letter grade based on score"""
        percentage = self.get_score_percentage()
        if percentage >= 90:
            return 'A+'
        elif percentage >= 80:
            return 'A'
        elif percentage >= 70:
            return 'B+'
        elif percentage >= 60:
            return 'B'
        elif percentage >= 50:
            return 'C+'
        elif percentage >= 40:
            return 'C'
        elif percentage >= 30:
            return 'D'
        else:
            return 'F'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'company_size_score': self.company_size_score,
            'industry_score': self.industry_score,
            'employee_level_score': self.employee_level_score,
            'location_score': self.location_score,
            'total_score': self.total_score,
            'max_possible_score': self.max_possible_score,
            'min_possible_score': self.min_possible_score,
            'score_percentage': self.get_score_percentage(),
            'score_grade': self.get_score_grade(),
            'company_size_match': self.company_size_match,
            'industry_match': self.industry_match,
            'employee_level_match': self.employee_level_match,
            'location_match': self.location_match,
            'scoring_timestamp': self.scoring_timestamp.isoformat() if self.scoring_timestamp else None,
            'cvr_data': self.cvr_data.to_dict() if self.cvr_data else None
        }


class CVRLeadScorer:
    """Service for scoring leads using CVR API data and ICP criteria"""
    
    def __init__(self, icp_criteria: Optional[ICPCriteria] = None):
        self.icp = icp_criteria or ICPCriteria()
        self.client = cvr_client
    
    def score_lead(self, lead: Lead, cvr_number: Optional[str] = None) -> LeadScoreBreakdown:
        """
        Score a lead against ICP criteria
        
        Args:
            lead: Lead instance to score
            cvr_number: Optional CVR number if not extractable from lead data
            
        Returns:
            LeadScoreBreakdown with detailed scoring information
        """
        logger.info(f"Scoring lead: {lead.full_name} from {lead.company}")
        
        # Initialize scores (1 point baseline for each criteria)
        company_size_score = 1
        industry_score = 1
        employee_level_score = 1
        location_score = 1
        
        # Initialize match flags
        company_size_match = False
        industry_match = False
        employee_level_match = False
        location_match = False
        
        cvr_data = None
        
        # Try to get CVR data if we have a CVR number
        if cvr_number or self._extract_cvr_from_lead(lead):
            cvr_to_use = cvr_number or self._extract_cvr_from_lead(lead)
            try:
                cvr_data = self.client.lookup_by_cvr(cvr_to_use)
                if cvr_data:
                    logger.info(f"Found CVR data for {lead.company}: {cvr_data.company_name}")
            except CVRAPIError as e:
                logger.warning(f"Failed to get CVR data for {lead.company}: {e}")
        
        # Score company size
        employee_count = self._get_employee_count(lead, cvr_data)
        if employee_count and employee_count >= self.icp.min_employees:
            company_size_score = 3
            company_size_match = True
            logger.info(f"Company size match: {employee_count} employees >= {self.icp.min_employees}")
        
        # Score industry
        industry = self._get_industry(lead, cvr_data)
        if industry and self._matches_target_industry(industry):
            industry_score = 3
            industry_match = True
            logger.info(f"Industry match: {industry}")
        
        # Score employee level (job title)
        if self._matches_target_employee_level(lead.title):
            employee_level_score = 3
            employee_level_match = True
            logger.info(f"Employee level match: {lead.title}")
        
        # Score location
        location = self._get_location(lead, cvr_data)
        if location and self._matches_target_location(location):
            location_score = 3
            location_match = True
            logger.info(f"Location match: {location}")
        
        # Calculate total score
        total_score = company_size_score + industry_score + employee_level_score + location_score
        
        logger.info(f"Lead {lead.full_name} scored {total_score}/12")
        
        return LeadScoreBreakdown(
            company_size_score=company_size_score,
            industry_score=industry_score,
            employee_level_score=employee_level_score,
            location_score=location_score,
            total_score=total_score,
            company_size_match=company_size_match,
            industry_match=industry_match,
            employee_level_match=employee_level_match,
            location_match=location_match,
            cvr_data=cvr_data
        )
    
    def score_and_update_lead(self, lead: Lead, cvr_number: Optional[str] = None) -> LeadScoreBreakdown:
        """Score a lead and update the lead_score field in the database"""
        score_breakdown = self.score_lead(lead, cvr_number)
        
        # Update the lead with the new score
        lead.lead_score = score_breakdown.total_score
        
        # Update other fields if we have CVR data
        if score_breakdown.cvr_data:
            cvr_data = score_breakdown.cvr_data
            if not lead.employees and cvr_data.employee_count:
                lead.employees = cvr_data.employee_count
            if not lead.industry and cvr_data.industry_text:
                lead.industry = cvr_data.industry_text
            if not lead.website and cvr_data.website:
                lead.website = cvr_data.website
            if not lead.phone and cvr_data.phone:
                lead.phone = cvr_data.phone
        
        lead.save()
        logger.info(f"Updated lead {lead.full_name} with score {score_breakdown.total_score}")
        
        return score_breakdown
    
    def bulk_score_leads(self, leads: List[Lead]) -> List[LeadScoreBreakdown]:
        """Score multiple leads in bulk"""
        results = []
        for lead in leads:
            try:
                score_breakdown = self.score_and_update_lead(lead)
                results.append(score_breakdown)
            except Exception as e:
                logger.error(f"Failed to score lead {lead.full_name}: {e}")
                # Create a minimal score breakdown for failed leads
                results.append(LeadScoreBreakdown(
                    company_size_score=1,
                    industry_score=1,
                    employee_level_score=1,
                    location_score=1,
                    total_score=4,
                    company_size_match=False,
                    industry_match=False,
                    employee_level_match=False,
                    location_match=False
                ))
        return results
    
    def _extract_cvr_from_lead(self, lead: Lead) -> Optional[str]:
        """Try to extract CVR number from lead data"""
        # Look in company name, description, or other fields for CVR pattern
        import re
        cvr_pattern = r'\b\d{8}\b'  # 8-digit number pattern
        
        text_fields = [lead.company, lead.description, lead.website]
        for field in text_fields:
            if field:
                matches = re.findall(cvr_pattern, field)
                if matches:
                    return matches[0]
        return None
    
    def _get_employee_count(self, lead: Lead, cvr_data: Optional[CVRCompanyData]) -> Optional[int]:
        """Get employee count from lead or CVR data"""
        if cvr_data and cvr_data.employee_count:
            return cvr_data.employee_count
        return lead.employees
    
    def _get_industry(self, lead: Lead, cvr_data: Optional[CVRCompanyData]) -> Optional[str]:
        """Get industry from lead or CVR data"""
        if cvr_data and cvr_data.industry_text:
            return cvr_data.industry_text
        return lead.industry
    
    def _get_location(self, lead: Lead, cvr_data: Optional[CVRCompanyData]) -> Optional[str]:
        """Get location from lead or CVR data"""
        if cvr_data and cvr_data.city:
            return cvr_data.city
        return lead.city
    
    def _matches_target_industry(self, industry: str) -> bool:
        """Check if industry matches target industries"""
        if not industry:
            return False
        
        industry_lower = industry.lower()
        for target in self.icp.target_industries:
            if target.lower() in industry_lower:
                return True
        return False
    
    def _matches_target_employee_level(self, title: str) -> bool:
        """Check if job title indicates manager+ level"""
        if not title:
            return False
        
        title_lower = title.lower()
        for level in self.icp.target_employee_levels:
            if level.lower() in title_lower:
                return True
        return False
    
    def _matches_target_location(self, location: str) -> bool:
        """Check if location matches target cities"""
        if not location:
            return False
        
        location_lower = location.lower()
        for city in self.icp.target_cities:
            if city.lower() in location_lower:
                return True
        return False


def populate_lead_from_cvr(lead: Lead, cvr_number: str) -> bool:
    """
    Populate lead fields with data from CVR API
    
    Args:
        lead: Lead instance to populate
        cvr_number: CVR number to lookup
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Populating lead {lead.id} with CVR data for {cvr_number}")
        
        # Fetch CVR data
        cvr_data = cvr_client.lookup_by_cvr(cvr_number)
        if not cvr_data:
            logger.warning(f"No CVR data found for {cvr_number}")
            return False
        
        # Update lead fields with CVR data
        if cvr_data.company_name and not lead.company:
            lead.company = cvr_data.company_name
            
        if cvr_data.industry_text and not lead.industry:
            lead.industry = cvr_data.industry_text
            
        if cvr_data.employee_count and not lead.employees:
            lead.employees = cvr_data.employee_count
            
        if cvr_data.annual_revenue and not lead.annual_revenue:
            lead.annual_revenue = Decimal(str(cvr_data.annual_revenue))
            
        # Update address fields if not already set
        if cvr_data.address and not lead.street:
            lead.street = cvr_data.address
            
        if cvr_data.city and not lead.city:
            lead.city = cvr_data.city
            
        if cvr_data.postal_code and not lead.postal_code:
            lead.postal_code = cvr_data.postal_code
            
        if cvr_data.phone and not lead.phone:
            lead.phone = cvr_data.phone
            
        if cvr_data.website and not lead.website:
            lead.website = cvr_data.website
            
        # Set CVR fields
        lead.cvr_number = cvr_number
        lead.cvr_last_updated = timezone.now()
        
        # Save the lead
        lead.save()
        
        logger.info(f"Successfully populated lead {lead.id} with CVR data")
        return True
        
    except Exception as e:
        logger.error(f"Failed to populate lead {lead.id} with CVR data: {e}")
        return False


def create_lead_from_cvr(cvr_number: str, assigned_to, created_by, **extra_fields) -> Optional[Lead]:
    """
    Create a new lead from CVR data
    
    Args:
        cvr_number: CVR number to lookup
        assigned_to: User to assign the lead to
        created_by: User creating the lead
        **extra_fields: Additional fields to set on the lead
        
    Returns:
        Created Lead instance or None if failed
    """
    try:
        logger.info(f"Creating lead from CVR data for {cvr_number}")
        
        # Fetch CVR data
        cvr_data = cvr_client.lookup_by_cvr(cvr_number)
        if not cvr_data:
            logger.warning(f"No CVR data found for {cvr_number}")
            return None
        
        # Create lead with CVR data
        lead_data = {
            'company': cvr_data.company_name,
            'industry': cvr_data.industry_text,
            'employees': cvr_data.employee_count,
            'street': cvr_data.address,
            'city': cvr_data.city,
            'postal_code': cvr_data.postal_code,
            'phone': cvr_data.phone,
            'website': cvr_data.website,
            'cvr_number': cvr_number,
            'cvr_last_updated': timezone.now(),
            'assigned_to': assigned_to,
            'created_by': created_by,
            'lead_source': 'cvr_lookup',
            'status': 'new',
        }
        
        # Add annual revenue if available
        if cvr_data.annual_revenue:
            lead_data['annual_revenue'] = Decimal(str(cvr_data.annual_revenue))
        
        # Override with any extra fields provided
        lead_data.update(extra_fields)
        
        # Create the lead
        lead = Lead.objects.create(**lead_data)
        
        # Score the lead
        scoring_service = CVRLeadScorer()
        scoring_service.score_lead(lead, cvr_number)
        
        logger.info(f"Successfully created lead {lead.id} from CVR data")
        return lead
        
    except Exception as e:
        logger.error(f"Failed to create lead from CVR data {cvr_number}: {e}")
        return None


# Default scorer instance
default_scorer = CVRLeadScorer()
