# Calendar Module Documentation

## Overview
The Calendar Module provides a comprehensive calendar view for managing tasks, calls, and meetings in the CRM system. It includes both account-level and user-level calendar views using the open-source FullCalendar.js library.

## Features

### 📅 Main Calendar View
- **URL**: `/calendar/`
- **Description**: Shows all tasks, calls, and meetings across the system
- **Filtering**: By account, user, and event types
- **Views**: Month, Week, Day, and List views

### 🏢 Account Calendar View  
- **URL**: `/calendar/account/{account_id}/`
- **Description**: Shows calendar events specific to an account
- **Access**: Available from account detail pages
- **Filtering**: By event types (tasks, calls, meetings)

### 👤 User Calendar View
- **URL**: `/calendar/user/{user_id}/`
- **Description**: Shows calendar events assigned to a specific user
- **Access**: Available from user dropdown menu ("My Calendar")
- **Features**: Business hours display, personal event filtering

## Technical Implementation

### Backend Components

#### Models
The calendar uses existing models from the `tasks` app:
- **Task**: Tasks with due dates (uses generic foreign key for relations)
- **Call**: Phone calls with scheduled datetime and related accounts/contacts
- **Meeting**: Meetings with start/end datetime and related accounts/contacts

#### Views (`calendar_app/views.py`)
- `CalendarView`: Main calendar template view
- `AccountCalendarView`: Account-specific calendar template view  
- `UserCalendarView`: User-specific calendar template view
- `calendar_events_api`: JSON API endpoint for calendar events

#### API Endpoint
- **URL**: `/calendar/api/events/`
- **Method**: GET
- **Parameters**:
  - `start`: Start date (ISO format)
  - `end`: End date (ISO format)
  - `account_id`: Filter by account (optional)
  - `user_id`: Filter by user (optional)  
  - `types[]`: Event types array (tasks, calls, meetings)

### Frontend Components

#### FullCalendar.js Integration
- **Library**: FullCalendar v6.1.9 (Open Source)
- **CDN**: https://cdn.jsdelivr.net/npm/fullcalendar@6.1.9/
- **Views**: Month, Week, Day, List
- **Features**: Event click, drag/drop, responsive design

#### Event Color Coding
- **Tasks**: By priority (High=Red, Medium=Orange, Low=Green)
- **Calls**: By status (Scheduled=Blue, In Progress=Orange, Completed=Green, etc.)
- **Meetings**: By status (Scheduled=Blue, In Progress=Orange, Completed=Green, etc.)

#### Event Details Modal
- Shows comprehensive event information
- Direct links to edit events
- Responsive design with Bootstrap

### Navigation Integration

#### Main Navigation
- Added to Activities dropdown: "Calendar View"
- Quick access to main calendar

#### User Menu
- Added "My Calendar" link to user dropdown
- Direct access to user-specific calendar

#### Account Details
- Added "Calendar" button to account detail pages
- Quick access to account-specific calendar

## Usage Examples

### Accessing Calendars
```python
# Main calendar
{% url 'calendar_app:calendar' %}

# Account calendar
{% url 'calendar_app:account_calendar' account.id %}

# User calendar  
{% url 'calendar_app:user_calendar' user.id %}
```

### API Usage
```javascript
// Load events for current month
fetch('/calendar/api/events/?start=2025-07-01&end=2025-07-31&types[]=tasks&types[]=calls&types[]=meetings')
  .then(response => response.json())
  .then(events => {
    // Process events
  });
```

## Management Commands

### Sample Data Creation
```bash
python manage.py create_calendar_sample_data --days 30 --count 10
```
- Creates sample tasks, calls, and meetings
- Useful for testing and demonstration
- Includes realistic datetime distribution

## Configuration

### Required Settings
```python
INSTALLED_APPS = [
    # ... other apps
    'calendar_app',
]
```

### URL Configuration
```python
# crm_system/urls.py
urlpatterns = [
    # ... other patterns
    path("calendar/", include("calendar_app.urls")),
]
```

## Responsive Design

### Mobile Support
- Responsive FullCalendar configuration
- Touch-friendly event interaction
- Collapsible filter panels
- Mobile-optimized modal dialogs

### Desktop Features
- Multiple view types (Month/Week/Day/List)
- Keyboard navigation
- Event drag and drop (future enhancement)
- Advanced filtering options

## Security Features

### Authentication
- All views require login (`LoginRequiredMixin`)
- User-specific data filtering
- Account-based access control

### Data Protection
- CSRF protection on all forms
- Proper permission checking
- SQL injection prevention through Django ORM

## Performance Optimizations

### Database Queries
- `select_related()` for assigned users
- Optimized date range filtering
- Indexed datetime fields

### Frontend
- Lazy loading of calendar events
- Efficient date range requests
- Minimal DOM manipulation

## Future Enhancements

### Planned Features
- Event drag and drop editing
- Recurring event support
- Calendar sharing and permissions
- Email reminders and notifications
- Integration with external calendar systems (Google Calendar, Outlook)
- Real-time updates via WebSockets

### Technical Improvements
- Caching for frequent queries
- Event categorization and tagging
- Advanced filtering and search
- Export to ICS format
- Calendar widget for dashboard

## Browser Compatibility

### Supported Browsers
- Chrome 90+ ✅
- Firefox 88+ ✅
- Safari 14+ ✅
- Edge 90+ ✅

### Features Used
- ES6 JavaScript
- Fetch API
- CSS Grid and Flexbox
- Bootstrap 5 components

## Troubleshooting

### Common Issues

#### Events Not Loading
1. Check API endpoint response in browser dev tools
2. Verify date format in requests (ISO 8601)
3. Check Django logs for database errors

#### Calendar Not Rendering
1. Verify FullCalendar.js CDN is accessible
2. Check browser console for JavaScript errors
3. Ensure Bootstrap CSS is loaded

#### Permission Errors
1. Verify user is authenticated
2. Check account/user access permissions
3. Review related object relationships

### Debug Mode
Enable Django debug mode to see detailed error messages:
```python
DEBUG = True
```

## Dependencies

### Python Packages
- Django 5.2.4+
- django-widget-tweaks (for form styling)

### JavaScript Libraries
- FullCalendar.js 6.1.9 (Open Source)
- Bootstrap 5.x
- Font Awesome 6.x (for icons)

### No Paid Dependencies
All libraries used are open source and free for commercial use, meeting the requirement of avoiding paid solutions.
