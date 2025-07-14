"""
API views for CVR-based lead scoring
"""
import logging
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from django.db import models

from .models import Lead
from .services.cvr_scoring import default_scorer, CVRLeadScorer, ICPCriteria
from .services.cvr_client import cvr_client, CVRAPIError


logger = logging.getLogger(__name__)


class BaseAPIView(View):
    """Base class for API views with common functionality"""
    
    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def json_response(self, data, status=200):
        """Return JSON response"""
        return JsonResponse(data, status=status)
    
    def error_response(self, message, status=400):
        """Return error response"""
        return JsonResponse({'error': message}, status=status)


class LeadScoreAPIView(BaseAPIView):
    """API view for scoring individual leads"""
    
    def post(self, request, lead_id):
        """Score a specific lead"""
        try:
            lead = get_object_or_404(Lead, pk=lead_id)
            
            # Get optional CVR number from request
            data = json.loads(request.body) if request.body else {}
            cvr_number = data.get('cvr_number')
            
            # Score the lead
            score_breakdown = default_scorer.score_and_update_lead(lead, cvr_number)
            
            logger.info(f"Scored lead {lead.full_name}: {score_breakdown.total_score}/12")
            
            return self.json_response({
                'success': True,
                'lead_id': lead.id,
                'lead_name': lead.full_name,
                'company': lead.company,
                'score_breakdown': score_breakdown.to_dict()
            })
            
        except json.JSONDecodeError:
            return self.error_response("Invalid JSON in request body")
        except Exception as e:
            logger.error(f"Error scoring lead {lead_id}: {e}")
            return self.error_response(f"Failed to score lead: {str(e)}", 500)
    
    def get(self, request, lead_id):
        """Get current score for a lead"""
        try:
            lead = get_object_or_404(Lead, pk=lead_id)
            
            return self.json_response({
                'lead_id': lead.id,
                'lead_name': lead.full_name,
                'company': lead.company,
                'current_score': lead.icp_score,
                'score_breakdown': lead.icp_score_breakdown,
                'cvr_number': lead.cvr_number,
                'cvr_last_updated': lead.cvr_last_updated.isoformat() if lead.cvr_last_updated else None
            })
            
        except Exception as e:
            logger.error(f"Error getting lead score {lead_id}: {e}")
            return self.error_response(f"Failed to get lead score: {str(e)}", 500)


class BulkLeadScoreAPIView(BaseAPIView):
    """API view for bulk scoring multiple leads"""
    
    def post(self, request):
        """Score multiple leads in bulk"""
        try:
            data = json.loads(request.body) if request.body else {}
            lead_ids = data.get('lead_ids', [])
            
            if not lead_ids:
                return self.error_response("No lead IDs provided")
            
            # Get leads
            leads = Lead.objects.filter(id__in=lead_ids)
            if not leads.exists():
                return self.error_response("No valid leads found")
            
            # Score leads in bulk
            score_results = default_scorer.bulk_score_leads(list(leads))
            
            # Prepare response
            results = []
            for lead, score_breakdown in zip(leads, score_results):
                results.append({
                    'lead_id': lead.id,
                    'lead_name': lead.full_name,
                    'company': lead.company,
                    'score_breakdown': score_breakdown.to_dict()
                })
            
            logger.info(f"Bulk scored {len(results)} leads")
            
            return self.json_response({
                'success': True,
                'scored_count': len(results),
                'results': results
            })
            
        except json.JSONDecodeError:
            return self.error_response("Invalid JSON in request body")
        except Exception as e:
            logger.error(f"Error bulk scoring leads: {e}")
            return self.error_response(f"Failed to score leads: {str(e)}", 500)


class CVRDataAPIView(BaseAPIView):
    """API view for fetching CVR data"""
    
    def get(self, request, lead_id):
        """Get CVR data for a lead"""
        try:
            lead = get_object_or_404(Lead, pk=lead_id)
            
            cvr_number = lead.cvr_number
            if not cvr_number:
                return self.error_response("No CVR number associated with this lead")
            
            # Fetch CVR data
            cvr_data = cvr_client.lookup_by_cvr(cvr_number)
            if not cvr_data:
                return self.error_response(f"No CVR data found for {cvr_number}")
            
            return self.json_response({
                'lead_id': lead.id,
                'cvr_number': cvr_number,
                'cvr_data': cvr_data.to_dict()
            })
            
        except CVRAPIError as e:
            return self.error_response(f"CVR API error: {str(e)}")
        except Exception as e:
            logger.error(f"Error fetching CVR data for lead {lead_id}: {e}")
            return self.error_response(f"Failed to fetch CVR data: {str(e)}", 500)
    
    def post(self, request, lead_id):
        """Update lead with CVR number and fetch data"""
        try:
            lead = get_object_or_404(Lead, pk=lead_id)
            data = json.loads(request.body) if request.body else {}
            
            cvr_number = data.get('cvr_number')
            if not cvr_number:
                return self.error_response("CVR number is required")
            
            # Validate CVR number format
            cvr_clean = ''.join(filter(str.isdigit, cvr_number))
            if len(cvr_clean) != 8:
                return self.error_response("CVR number must be 8 digits")
            
            # Update lead with CVR number
            lead.cvr_number = cvr_clean
            lead.save()
            
            # Fetch CVR data
            cvr_data = cvr_client.lookup_by_cvr(cvr_clean)
            if cvr_data:
                # Update lead with CVR data
                if not lead.employees and cvr_data.employee_count:
                    lead.employees = cvr_data.employee_count
                if not lead.industry and cvr_data.industry_text:
                    lead.industry = cvr_data.industry_text
                if not lead.website and cvr_data.website:
                    lead.website = cvr_data.website
                if not lead.phone and cvr_data.phone:
                    lead.phone = cvr_data.phone
                
                lead.cvr_last_updated = timezone.now()
                lead.save()
                
                return self.json_response({
                    'success': True,
                    'lead_id': lead.id,
                    'cvr_number': cvr_clean,
                    'cvr_data': cvr_data.to_dict(),
                    'updated_fields': ['employees', 'industry', 'website', 'phone']
                })
            else:
                return self.error_response(f"No CVR data found for {cvr_clean}")
            
        except json.JSONDecodeError:
            return self.error_response("Invalid JSON in request body")
        except CVRAPIError as e:
            return self.error_response(f"CVR API error: {str(e)}")
        except Exception as e:
            logger.error(f"Error updating CVR data for lead {lead_id}: {e}")
            return self.error_response(f"Failed to update CVR data: {str(e)}", 500)


class ICPConfigAPIView(BaseAPIView):
    """API view for managing ICP configuration"""
    
    def get(self, request):
        """Get current ICP configuration"""
        icp = ICPCriteria()
        return self.json_response({
            'min_employees': icp.min_employees,
            'target_industries': icp.target_industries,
            'target_cities': icp.target_cities,
            'target_employee_levels': icp.target_employee_levels,
            'scoring_info': {
                'min_score': 4,
                'max_score': 12,
                'points_per_match': 3,
                'points_per_miss': 1
            }
        })


class LeadScoreStatsAPIView(BaseAPIView):
    """API view for lead scoring statistics"""
    
    def get(self, request):
        """Get lead scoring statistics"""
        try:
            from django.db.models import Avg, Count, Max, Min
            
            # Get scoring statistics
            stats = Lead.objects.aggregate(
                total_leads=Count('id'),
                avg_score=Avg('icp_score'),
                min_score=Min('icp_score'),
                max_score=Max('icp_score'),
                scored_leads=Count('id', filter=models.Q(icp_score__gt=4))
            )
            
            # Get score distribution
            score_distribution = {}
            for score in range(4, 13):
                count = Lead.objects.filter(icp_score=score).count()
                score_distribution[str(score)] = count
            
            # Get top scoring leads
            top_leads = Lead.objects.filter(icp_score__gte=10).order_by('-icp_score')[:10]
            top_leads_data = [
                {
                    'id': lead.id,
                    'name': lead.full_name,
                    'company': lead.company,
                    'score': lead.icp_score,
                    'industry': lead.industry
                }
                for lead in top_leads
            ]
            
            return self.json_response({
                'statistics': stats,
                'score_distribution': score_distribution,
                'top_scoring_leads': top_leads_data
            })
            
        except Exception as e:
            logger.error(f"Error getting lead score stats: {e}")
            return self.error_response(f"Failed to get statistics: {str(e)}", 500)


class CVRLookupAPIView(BaseAPIView):
    """API view for CVR company lookup"""
    
    def post(self, request):
        """Look up company data by CVR number"""
        try:
            data = json.loads(request.body) if request.body else {}
            cvr_number = data.get('cvr_number')
            
            if not cvr_number:
                return self.error_response("CVR number is required", 400)
            
            # Clean CVR number
            cvr_clean = ''.join(filter(str.isdigit, cvr_number))
            if len(cvr_clean) != 8:
                return self.error_response("CVR number must be 8 digits", 400)
            
            # Lookup CVR data
            cvr_data = cvr_client.lookup_by_cvr(cvr_clean)
            
            if not cvr_data:
                return self.error_response("Company not found", 404)
            
            return self.json_response({
                'success': True,
                'cvr_data': cvr_data.to_dict(),
                'message': f'Found company: {cvr_data.company_name}'
            })
            
        except json.JSONDecodeError:
            return self.error_response("Invalid JSON", 400)
        except CVRAPIError as e:
            logger.error(f"CVR API error: {e}")
            return self.error_response(f"CVR API error: {str(e)}", 503)
        except Exception as e:
            logger.error(f"CVR lookup error: {e}")
            return self.error_response("Internal server error", 500)


class PopulateLeadFromCVRAPIView(BaseAPIView):
    """API view for populating lead data from CVR"""
    
    def post(self, request, lead_id):
        """Populate lead with CVR data"""
        try:
            lead = get_object_or_404(Lead, pk=lead_id)
            data = json.loads(request.body) if request.body else {}
            cvr_number = data.get('cvr_number') or lead.cvr_number
            
            if not cvr_number:
                return self.error_response("CVR number is required", 400)
            
            # Import the function
            from .services.cvr_scoring import populate_lead_from_cvr
            
            # Populate lead with CVR data
            success = populate_lead_from_cvr(lead, cvr_number)
            
            if success:
                # Return updated lead data
                return self.json_response({
                    'success': True,
                    'message': f'Lead {lead.id} updated with CVR data',
                    'lead': {
                        'id': lead.id,
                        'company': lead.company,
                        'industry': lead.industry,
                        'employees': lead.employees,
                        'annual_revenue': float(lead.annual_revenue) if lead.annual_revenue else None,
                        'address': lead.street,
                        'city': lead.city,
                        'postal_code': lead.postal_code,
                        'phone': lead.phone,
                        'website': lead.website,
                        'cvr_number': lead.cvr_number,
                        'icp_score': lead.icp_score,
                        'cvr_last_updated': lead.cvr_last_updated.isoformat() if lead.cvr_last_updated else None
                    }
                })
            else:
                return self.error_response("Failed to populate lead with CVR data", 500)
            
        except json.JSONDecodeError:
            return self.error_response("Invalid JSON", 400)
        except Exception as e:
            logger.error(f"Populate lead error: {e}")
            return self.error_response("Internal server error", 500)


class CreateLeadFromCVRAPIView(BaseAPIView):
    """API view for creating leads from CVR data"""
    
    def post(self, request):
        """Create a new lead from CVR data"""
        try:
            data = json.loads(request.body) if request.body else {}
            cvr_number = data.get('cvr_number')
            
            if not cvr_number:
                return self.error_response("CVR number is required", 400)
            
            # Check if lead already exists
            existing_lead = Lead.objects.filter(cvr_number=cvr_number).first()
            if existing_lead:
                return self.error_response(f"Lead already exists with CVR {cvr_number} (ID: {existing_lead.id})", 409)
            
            # Import the function
            from .services.cvr_scoring import create_lead_from_cvr
            
            # Create lead from CVR data
            lead = create_lead_from_cvr(
                cvr_number=cvr_number,
                assigned_to=request.user,
                created_by=request.user,
                **data.get('extra_fields', {})
            )
            
            if lead:
                return self.json_response({
                    'success': True,
                    'message': f'Lead created from CVR data',
                    'lead': {
                        'id': lead.id,
                        'company': lead.company,
                        'industry': lead.industry,
                        'employees': lead.employees,
                        'annual_revenue': float(lead.annual_revenue) if lead.annual_revenue else None,
                        'address': lead.street,
                        'city': lead.city,
                        'postal_code': lead.postal_code,
                        'phone': lead.phone,
                        'website': lead.website,
                        'cvr_number': lead.cvr_number,
                        'icp_score': lead.icp_score,
                        'cvr_last_updated': lead.cvr_last_updated.isoformat() if lead.cvr_last_updated else None
                    }
                }, 201)
            else:
                return self.error_response("Failed to create lead from CVR data", 500)
            
        except json.JSONDecodeError:
            return self.error_response("Invalid JSON", 400)
        except Exception as e:
            logger.error(f"Create lead from CVR error: {e}")
            return self.error_response("Internal server error", 500)


# Standalone function views for simpler endpoints
@login_required
@require_http_methods(["POST"])
@csrf_exempt
def score_all_leads(request):
    """Score all leads in the database"""
    try:
        # Get all leads without scores or with old scores
        leads = Lead.objects.filter(icp_score__lte=4)
        
        if not leads.exists():
            return JsonResponse({
                'success': True,
                'message': 'No leads need scoring',
                'scored_count': 0
            })
        
        # Score leads in batches
        batch_size = 50
        total_scored = 0
        
        for i in range(0, leads.count(), batch_size):
            batch = list(leads[i:i + batch_size])
            default_scorer.bulk_score_leads(batch)
            total_scored += len(batch)
            logger.info(f"Scored batch {i//batch_size + 1}: {len(batch)} leads")
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully scored {total_scored} leads',
            'scored_count': total_scored
        })
        
    except Exception as e:
        logger.error(f"Error scoring all leads: {e}")
        return JsonResponse({
            'error': f'Failed to score leads: {str(e)}'
        }, status=500)
