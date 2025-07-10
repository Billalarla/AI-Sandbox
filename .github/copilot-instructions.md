# CRM System - Copilot Instructions

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Overview
This is a comprehensive CRM (Customer Relationship Management) system built with Django, similar to SugarCRM. The system manages accounts, contacts, leads, opportunities, tasks, campaigns, and provides analytics dashboard.

## Architecture
- **Backend**: Django 5.2.4 with Python 3.10
- **Database**: SQLite (development), easily upgradeable to PostgreSQL
- **Frontend**: Django templates with Bootstrap 5 and Chart.js
- **Authentication**: Django's built-in auth system
- **Task Queue**: Celery with Redis (for background tasks)

## Key Applications
- `accounts`: Customer account management
- `contacts`: Contact information and relationships
- `leads`: Lead tracking and conversion
- `opportunities`: Sales opportunity management
- `tasks`: Task and meeting management
- `campaigns`: Marketing campaign tracking
- `dashboard`: Analytics and reporting

## Development Guidelines
1. Follow Django best practices and PEP 8 style guide
2. Use class-based views with proper mixins (LoginRequiredMixin)
3. Implement proper error handling and user feedback
4. Use Django's built-in pagination for list views
5. Add proper docstrings and comments
6. Use Django's form system and crispy forms for styling
7. Implement proper permissions and access control
8. Use select_related and prefetch_related for query optimization

## Database Models
- All models include created_at, updated_at, created_by, and assigned_to fields
- Use proper foreign key relationships with CASCADE/SET_NULL as appropriate
- Implement __str__ methods and get_absolute_url methods
- Use choices for status fields and other enumerations

## Frontend Guidelines
- Use Bootstrap 5 for responsive design
- Implement proper CRUD operations for all entities
- Use Chart.js for data visualization
- Implement proper form validation and error display
- Use Font Awesome icons consistently
- Make the interface mobile-friendly

## Security Considerations
- Always use LoginRequiredMixin for authenticated views
- Implement proper CSRF protection
- Use Django's built-in permission system
- Sanitize user inputs properly
- Use Django's built-in security features

## Testing
- Write unit tests for models and views
- Test form validation and business logic
- Test user permissions and access control
- Use Django's test client for integration tests
