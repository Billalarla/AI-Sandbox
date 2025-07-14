# CVR API Lead Scoring Configuration

This module provides CVR API integration for lead scoring based on Ideal Customer Profile (ICP) criteria.

## Features
- Fetches company data from cvrapi.dk using CVR numbers
- Scores leads against configurable ICP criteria
- Supports both manual and automatic scoring
- Provides detailed scoring breakdown

## ICP Criteria
- **Company Size**: 200+ employees (3 points if match, 1 if not)
- **Industry**: FMCG, Retail, SaaS (3 points if match, 1 if not)  
- **Employee Level**: Manager+ (3 points if match, 1 if not)
- **Location**: Copenhagen or Aarhus (3 points if match, 1 if not)

**Total Score Range**: 4-12 points

## Usage
```python
from leads.services.cvr_scoring import CVRLeadScorer

scorer = CVRLeadScorer()
score_data = scorer.score_lead(lead_instance)
print(f"Lead score: {score_data['total_score']}")
```

## API Endpoints
- `POST /api/leads/{id}/score/` - Score a specific lead
- `POST /api/leads/bulk-score/` - Score multiple leads
- `GET /api/leads/{id}/cvr-data/` - Get CVR data for a lead

## Management Commands
- `python manage.py score_all_leads` - Score all leads in the database
- `python manage.py update_cvr_data` - Refresh CVR data for all leads
