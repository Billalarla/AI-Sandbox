"""
Django management command to test CVR API functionality
Usage: python manage.py test_cvr_api [cvr_number]
"""
from django.core.management.base import BaseCommand
from leads.services.cvr_client import cvr_client
from leads.services.cvr_scoring import CVRLeadScorer
from leads.models import Lead
import json


class Command(BaseCommand):
    help = 'Test CVR API functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            'cvr_number',
            nargs='?',
            default='42718033',
            help='CVR number to test (default: 42718033 for Flatpay)'
        )
        parser.add_argument(
            '--create-lead',
            action='store_true',
            help='Create a lead from CVR data if lookup succeeds'
        )

    def handle(self, *args, **options):
        cvr_number = options['cvr_number']
        
        self.stdout.write(
            self.style.SUCCESS(f'🔍 Testing CVR API for CVR: {cvr_number}')
        )
        self.stdout.write('=' * 60)
        
        # Test CVR lookup
        try:
            cvr_data = cvr_client.lookup_by_cvr(cvr_number)
            
            if cvr_data:
                self.stdout.write(
                    self.style.SUCCESS('✅ CVR Data Retrieved Successfully!')
                )
                self.stdout.write(f'Company Name: {cvr_data.company_name}')
                self.stdout.write(f'Industry: {cvr_data.industry_text} (Code: {cvr_data.industry_code})')
                self.stdout.write(f'Employees: {cvr_data.employee_count}')
                self.stdout.write(f'Annual Revenue: {cvr_data.annual_revenue}')
                self.stdout.write(f'Address: {cvr_data.address}')
                self.stdout.write(f'City: {cvr_data.city}')
                self.stdout.write(f'Postal Code: {cvr_data.postal_code}')
                self.stdout.write(f'Phone: {cvr_data.phone}')
                self.stdout.write(f'Website: {cvr_data.website}')
                self.stdout.write(f'Status: {cvr_data.status}')
                self.stdout.write('')
                
                # Test scoring if we have the data
                if options['create_lead']:
                    self.stdout.write('🏢 Creating test lead from CVR data...')
                    
                    from django.contrib.auth.models import User
                    from leads.services.cvr_scoring import create_lead_from_cvr
                    
                    user = User.objects.first()
                    if user:
                        lead = create_lead_from_cvr(
                            cvr_number=cvr_number,
                            assigned_to=user,
                            created_by=user,
                            first_name='Test',
                            last_name='Contact',
                            email=f'test@{cvr_data.company_name.lower().replace(" ", "")}.dk',
                            title='Manager'
                        )
                        
                        if lead:
                            self.stdout.write(
                                self.style.SUCCESS(f'✅ Lead created successfully! (ID: {lead.id})')
                            )
                            self.stdout.write(f'ICP Score: {lead.icp_score}/12 points')
                        else:
                            self.stdout.write(
                                self.style.ERROR('❌ Failed to create lead')
                            )
                    else:
                        self.stdout.write(
                            self.style.ERROR('❌ No users found in database')
                        )
                
            else:
                self.stdout.write(
                    self.style.ERROR('❌ No CVR data found')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ CVR API Error: {str(e)}')
            )
        
        # Test existing lead scoring
        self.stdout.write('')
        self.stdout.write('🎯 Testing existing lead scoring...')
        
        try:
            lead = Lead.objects.filter(cvr_number=cvr_number).first()
            
            if lead:
                scorer = CVRLeadScorer()
                score_breakdown = scorer.score_lead(lead)
                
                self.stdout.write(f'📊 Scoring Results for {lead.company}:')
                self.stdout.write(f'  Company Size (≥200 employees): {score_breakdown.company_size_score} points {"✅" if score_breakdown.company_size_match else "❌"}')
                self.stdout.write(f'  Industry Match: {score_breakdown.industry_score} points {"✅" if score_breakdown.industry_match else "❌"}')
                self.stdout.write(f'  Employee Level: {score_breakdown.employee_level_score} points {"✅" if score_breakdown.employee_level_match else "❌"}')
                self.stdout.write(f'  Location Match: {score_breakdown.location_score} points {"✅" if score_breakdown.location_match else "❌"}')
                self.stdout.write(f'  🏆 Total Score: {score_breakdown.total_score}/12 points')
                
                # Calculate grade
                if score_breakdown.total_score >= 10:
                    grade = "A+ (Excellent Match)"
                elif score_breakdown.total_score >= 8:
                    grade = "A (Good Match)"
                elif score_breakdown.total_score >= 6:
                    grade = "B (Fair Match)"
                else:
                    grade = "C (Poor Match)"
                
                self.stdout.write(f'  📈 Grade: {grade}')
            else:
                self.stdout.write(f'❌ No lead found with CVR {cvr_number}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Scoring Error: {str(e)}')
            )
        
        self.stdout.write('')
        self.stdout.write('✨ CVR API test completed!')
