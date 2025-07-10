# CRM System - Customer Relationship Management

A comprehensive CRM system built with Django, similar to SugarCRM, featuring account management, lead tracking, sales opportunities, task management, and analytics dashboard.

## 🚀 Features

### Core CRM Functionality
- **Account Management**: Manage customer accounts with complete contact information
- **Contact Management**: Store and organize contact details with relationships
- **Lead Management**: Track potential customers through the sales pipeline
- **Opportunity Management**: Manage sales opportunities with probability tracking
- **Task & Activity Management**: Schedule and track tasks, meetings, and activities
- **Campaign Management**: Create and track marketing campaigns with ROI analysis

### Analytics & Reporting
- **Interactive Dashboard**: Real-time analytics with charts and KPIs
- **Sales Pipeline Visualization**: Track opportunities through sales stages
- **Lead Conversion Analytics**: Monitor lead-to-customer conversion rates
- **Monthly Sales Trends**: Visualize sales performance over time
- **Campaign ROI Tracking**: Measure marketing campaign effectiveness

### User Experience
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Role-based Access Control**: Secure access with user permissions
- **Modern UI**: Clean, intuitive interface with Bootstrap 5
- **Real-time Notifications**: Stay updated with system messages
- **Advanced Search & Filtering**: Find records quickly and efficiently

## 🛠️ Technology Stack

- **Backend**: Django 5.2.4 (Python 3.10+)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Django Templates, Bootstrap 5, Chart.js
- **Authentication**: Django's built-in auth system
- **Task Queue**: Celery with Redis
- **Forms**: Django Forms with Crispy Forms
- **Icons**: Font Awesome 6

## 📋 Prerequisites

- Python 3.10 or higher
- Virtual environment (recommended)
- Git

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd crm-system
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser!

## 📊 Default Login
After creating a superuser, you can access the admin interface at `/admin/` and the main CRM interface at the root URL.

## 🏗️ Project Structure

```
crm_system/
├── accounts/           # Account management
├── contacts/           # Contact management  
├── leads/             # Lead tracking
├── opportunities/     # Sales opportunities
├── tasks/            # Task & meeting management
├── campaigns/        # Marketing campaigns
├── dashboard/        # Analytics & reporting
├── templates/        # HTML templates
├── static/          # CSS, JS, images
├── crm_system/      # Project settings
└── manage.py        # Django management script
```

## 🎯 Key Models

### Account
- Company information and billing details
- Industry classification and revenue tracking
- Assigned sales representatives

### Contact  
- Personal and professional information
- Account relationships and reporting structure
- Communication preferences

### Lead
- Potential customer information
- Lead source tracking and status management
- Conversion workflow

### Opportunity
- Sales deal tracking with amount and probability
- Sales stage progression
- Expected close dates and next steps

### Task & Meeting
- Activity scheduling and tracking
- Priority and status management
- Generic relationships to any CRM object

### Campaign
- Marketing campaign management
- Budget tracking and ROI calculation
- Target audience management

## 🔧 Configuration

### Environment Variables
Create a `.env` file for production settings:
```
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=your-database-url
REDIS_URL=your-redis-url
```

### Production Deployment
1. Set `DEBUG = False` in settings
2. Configure a production database (PostgreSQL recommended)
3. Set up Redis for Celery tasks
4. Configure static file serving
5. Set up proper logging
6. Configure email backend for notifications

## 🧪 Running Tests
```bash
python manage.py test
```

## 📈 Usage Examples

### Creating an Account
1. Navigate to Accounts → Create Account
2. Fill in company information
3. Assign to a sales representative
4. Save and start adding contacts

### Managing Leads
1. Go to Leads → Create Lead
2. Enter prospect information
3. Set lead source and status
4. Convert qualified leads to accounts/contacts

### Tracking Opportunities
1. Navigate to Opportunities → Create Opportunity
2. Link to existing account and contact
3. Set amount, probability, and close date
4. Track through sales stages

### Dashboard Analytics
- View real-time KPIs and metrics
- Analyze sales pipeline by stage
- Monitor lead conversion rates
- Track monthly sales trends

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the code comments and docstrings

## 🚀 Future Enhancements

- [ ] Email integration for automated communications
- [ ] Document management and file uploads
- [ ] Advanced reporting with custom report builder
- [ ] API endpoints for mobile app integration
- [ ] Integration with popular email marketing tools
- [ ] Advanced workflow automation
- [ ] Multi-currency support
- [ ] Territory management
- [ ] Forecasting and quota management
- [ ] Social media integration

---

**Built with ❤️ using Django and Python**
