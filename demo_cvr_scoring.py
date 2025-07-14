"""
CVR Lead Scoring Demo Script

This script demonstrates how the CVR API integration and lead scoring works
without requiring database migration.

Run this script to see how leads would be scored based on ICP criteria.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_system.settings')
django.setup()

from leads.models import Lead
from leads.services.cvr_scoring import CVRLeadScorer, ICPCriteria, LeadScoreBreakdown
from leads.services.cvr_client import CVRCompanyData


def demo_cvr_scoring():
    """Demonstrate CVR-based lead scoring"""
    print("="*60)
    print("CVR LEAD SCORING DEMONSTRATION")
    print("="*60)
    
    # Define ICP criteria
    icp_criteria = ICPCriteria(
        min_employees=200,
        target_industries=['FMCG', 'Retail', 'SaaS', 'Software', 'Technology'],
        target_cities=['Copenhagen', 'København', 'Aarhus', 'Århus'],
        target_employee_levels=['Manager', 'Director', 'VP', 'CEO', 'CTO', 'Head of']
    )
    
    print("\nICP CRITERIA:")
    print(f"• Minimum employees: {icp_criteria.min_employees}")
    print(f"• Target industries: {', '.join(icp_criteria.target_industries)}")
    print(f"• Target cities: {', '.join(icp_criteria.target_cities)}")
    print(f"• Target employee levels: Manager+ positions")
    
    # Create scorer
    scorer = CVRLeadScorer(icp_criteria)
    
    # Create sample leads for demonstration
    sample_leads = [
        {
            'name': 'Lars Nielsen',
            'title': 'VP of Sales',
            'company': 'Danish Retail Group A/S',
            'city': 'Copenhagen',
            'industry': 'Retail',
            'employees': 250,
            'cvr': '12345678'
        },
        {
            'name': 'Anna Petersen',
            'title': 'Marketing Coordinator',
            'company': 'Small Consulting ApS',
            'city': 'Aalborg',
            'industry': 'Consulting',
            'employees': 15,
            'cvr': '87654321'
        },
        {
            'name': 'Michael Andersen',
            'title': 'Chief Technology Officer',
            'company': 'TechSoft Solutions A/S',
            'city': 'Aarhus',
            'industry': 'Software',
            'employees': 320,
            'cvr': '11223344'
        },
        {
            'name': 'Sarah Johnson',
            'title': 'Sales Representative',
            'company': 'International Corp',
            'city': 'London',
            'industry': 'Manufacturing',
            'employees': 150,
            'cvr': None
        }
    ]
    
    print("\n" + "="*60)
    print("LEAD SCORING RESULTS")
    print("="*60)
    
    for i, lead_data in enumerate(sample_leads, 1):
        print(f"\nLEAD #{i}: {lead_data['name']}")
        print("-" * 40)
        print(f"Title: {lead_data['title']}")
        print(f"Company: {lead_data['company']}")
        print(f"Location: {lead_data['city']}")
        print(f"Industry: {lead_data['industry']}")
        print(f"Employees: {lead_data['employees']}")
        print(f"CVR: {lead_data['cvr'] or 'Not available'}")
        
        # Mock CVR data for demonstration
        cvr_data = None
        if lead_data['cvr']:
            cvr_data = CVRCompanyData(
                cvr_number=lead_data['cvr'],
                company_name=lead_data['company'],
                industry_code='47110',
                industry_text=lead_data['industry'],
                employee_count=lead_data['employees'],
                annual_revenue=None,
                address='Sample Street 123',
                city=lead_data['city'],
                postal_code='1000',
                phone='+45 12 34 56 78',
                email='info@example.dk',
                website='https://example.dk',
                status='active',
                established_date='2010-01-01',
                legal_form='A/S'
            )
        
        # Calculate scores manually for demo
        company_size_score = 3 if lead_data['employees'] >= icp_criteria.min_employees else 1
        industry_score = 3 if any(industry.lower() in lead_data['industry'].lower() for industry in icp_criteria.target_industries) else 1
        employee_level_score = 3 if any(level.lower() in lead_data['title'].lower() for level in icp_criteria.target_employee_levels) else 1
        location_score = 3 if any(city.lower() in lead_data['city'].lower() for city in icp_criteria.target_cities) else 1
        
        total_score = company_size_score + industry_score + employee_level_score + location_score
        
        # Create score breakdown
        score_breakdown = LeadScoreBreakdown(
            company_size_score=company_size_score,
            industry_score=industry_score,
            employee_level_score=employee_level_score,
            location_score=location_score,
            total_score=total_score,
            company_size_match=company_size_score == 3,
            industry_match=industry_score == 3,
            employee_level_match=employee_level_score == 3,
            location_match=location_score == 3,
            cvr_data=cvr_data
        )
        
        print(f"\nSCORING BREAKDOWN:")
        print(f"• Company Size: {company_size_score}/3 ({'✓' if company_size_score == 3 else '✗'})")
        print(f"• Industry Match: {industry_score}/3 ({'✓' if industry_score == 3 else '✗'})")
        print(f"• Employee Level: {employee_level_score}/3 ({'✓' if employee_level_score == 3 else '✗'})")
        print(f"• Location Match: {location_score}/3 ({'✓' if location_score == 3 else '✗'})")
        print(f"\nTOTAL SCORE: {total_score}/12 ({score_breakdown.get_score_percentage():.1f}%)")
        print(f"GRADE: {score_breakdown.get_score_grade()}")
        
        # Recommendation
        if total_score >= 10:
            print("🎯 RECOMMENDATION: HIGH PRIORITY - Excellent ICP match!")
        elif total_score >= 7:
            print("⚡ RECOMMENDATION: MEDIUM PRIORITY - Good potential")
        else:
            print("📋 RECOMMENDATION: LOW PRIORITY - Limited ICP match")
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("This demonstrates how leads are scored against your ICP criteria:")
    print("• Each criterion can score 1-3 points")
    print("• Total possible score: 4-12 points")
    print("• CVR API provides enriched company data")
    print("• Automatic scoring helps prioritize leads")
    
    print(f"\nTO IMPLEMENT:")
    print("1. Get CVR API key from https://cvrapi.dk/")
    print("2. Set CVR_API_KEY in Django settings")
    print("3. Run: python manage.py score_all_leads")
    print("4. Use API endpoints for real-time scoring")
    
    # Show available API endpoints
    print(f"\nAVAILABLE API ENDPOINTS:")
    print("• POST /leads/api/{id}/score/ - Score specific lead")
    print("• POST /leads/api/bulk-score/ - Score multiple leads")
    print("• GET /leads/api/{id}/cvr-data/ - Get CVR data")
    print("• GET /leads/api/icp-config/ - View ICP configuration")
    print("• GET /leads/api/score-stats/ - Scoring statistics")


if __name__ == "__main__":
    try:
        demo_cvr_scoring()
    except Exception as e:
        print(f"Error running demo: {e}")
        print("Make sure Django is properly configured and all dependencies are installed.")
