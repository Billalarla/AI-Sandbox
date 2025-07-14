#!/usr/bin/env python
"""
Create a manual test lead for Flatpay ApS with known data
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_system.settings')
django.setup()

from leads.models import Lead
from leads.services.cvr_scoring import CVRLeadScorer
from django.contrib.auth.models import User
from decimal import Decimal

def create_flatpay_lead_manual():
    """Create a test lead for Flatpay ApS with manual data"""
    print("🏢 Creating Manual Test Lead for Flatpay ApS")
    print("=" * 60)
    
    # Get the first user
    user = User.objects.first()
    if not user:
        print("❌ No users found. Please create a user first.")
        return None
    
    # Check if lead already exists
    existing_lead = Lead.objects.filter(company__icontains="Flatpay").first()
    if existing_lead:
        print(f"📋 Flatpay lead already exists (ID: {existing_lead.id})")
        return existing_lead
    
    # Create lead with manual data (based on publicly available info)
    lead_data = {
        'first_name': 'Christian',
        'last_name': 'Stenderup', 
        'email': 'christian@flatpay.dk',
        'company': 'Flatpay ApS',
        'title': 'CEO',
        'phone': '+45 89 88 66 80',
        'website': 'https://flatpay.dk',
        'industry': 'Financial Technology',
        'employees': 50,  # Estimated
        'annual_revenue': Decimal('10000000'),  # Estimated 10M DKK
        'street': 'Gammeltorv 8',
        'city': 'Copenhagen',
        'postal_code': '1457',
        'country': 'Denmark',
        'cvr_number': '42718033',
        'lead_source': 'manual_entry',
        'status': 'new',
        'assigned_to': user,
        'created_by': user,
        'description': 'Test lead for Flatpay ApS - Danish payment technology company'
    }
    
    try:
        lead = Lead.objects.create(**lead_data)
        print("✅ Lead created successfully!")
        print(f"Lead ID: {lead.id}")
        print(f"Company: {lead.company}")
        print(f"Industry: {lead.industry}")
        print(f"Employees: {lead.employees}")
        print(f"Annual Revenue: {lead.annual_revenue}")
        print(f"Address: {lead.street}, {lead.city} {lead.postal_code}")
        print(f"Phone: {lead.phone}")
        print(f"Website: {lead.website}")
        print(f"CVR Number: {lead.cvr_number}")
        print()
        
        # Score the lead
        scorer = CVRLeadScorer()
        score_breakdown = scorer.score_lead(lead)
        
        print("📊 ICP Score Breakdown:")
        print(f"  Company Size (≥200 employees): {score_breakdown.company_size_score} points ({'✅' if score_breakdown.company_size_match else '❌'})")
        print(f"  Industry Match: {score_breakdown.industry_score} points ({'✅' if score_breakdown.industry_match else '❌'})")
        print(f"  Employee Level: {score_breakdown.employee_level_score} points ({'✅' if score_breakdown.employee_level_match else '❌'})")
        print(f"  Location Match: {score_breakdown.location_score} points ({'✅' if score_breakdown.location_match else '❌'})")
        print(f"  🏆 Total Score: {score_breakdown.total_score}/12 points")
        
        # Calculate grade
        if score_breakdown.total_score >= 10:
            grade = "A+ (Excellent Match)"
        elif score_breakdown.total_score >= 8:
            grade = "A (Good Match)"
        elif score_breakdown.total_score >= 6:
            grade = "B (Fair Match)"
        else:
            grade = "C (Poor Match)"
        
        print(f"  📈 Grade: {grade}")
        print()
        
        # Update lead with scoring results
        lead.icp_score = score_breakdown.total_score
        lead.icp_score_breakdown = {
            'company_size_score': score_breakdown.company_size_score,
            'industry_score': score_breakdown.industry_score,
            'employee_level_score': score_breakdown.employee_level_score,
            'location_score': score_breakdown.location_score,
            'total_score': score_breakdown.total_score,
            'company_size_match': score_breakdown.company_size_match,
            'industry_match': score_breakdown.industry_match,
            'employee_level_match': score_breakdown.employee_level_match,
            'location_match': score_breakdown.location_match,
        }
        lead.save()
        
        print("✅ Lead scoring completed and saved!")
        return lead
        
    except Exception as e:
        print(f"❌ Failed to create lead: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Manual Flatpay Lead Creation")
    print("=" * 60)
    print()
    
    lead = create_flatpay_lead_manual()
    
    if lead:
        print()
        print("🎉 Success! Flatpay lead created and scored.")
        print(f"   View in admin: /admin/leads/lead/{lead.id}/")
        print(f"   Lead detail page: /leads/{lead.id}/")
    
    print()
    print("✨ Manual lead creation completed!")
