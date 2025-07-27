# AidConnect - Humanitarian Aid Management System

AidConnect is a comprehensive management information system (MIS) designed for humanitarian aid organizations to manage beneficiaries, cases, assessments, and field operations efficiently.

## Project Overview

AidConnect provides a role-based platform for humanitarian organizations to:
- Manage beneficiary information
- Track cases and interventions
- Conduct and record assessments
- Generate reports and analytics
- Coordinate field operations

## Features

- **Role-based Access Control**: Different dashboards and permissions for Administrators, Case Managers, and Field Officers
- **Beneficiary Management**: Track personal information and history of services provided
- **Case Management**: Create and manage cases linked to beneficiaries
- **Assessment System**: Create, assign, and record structured assessments
- **Customizable Reports**: Generate and export reports with full details and summary tables
- **Export Functionality**: Export data to Excel and PDF formats
- **API Access**: RESTful API with Swagger documentation
- **Responsive Design**: Works on desktop and mobile devices

## Technology Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: SQLite (default, configurable)
- **Frontend**: Bootstrap 5, Django Templates
- **API Documentation**: drf-yasg (Swagger)
- **Authentication**: Django's built-in authentication system

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/aidconnect.git
   cd aidconnect
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```
   python manage.py migrate
   ```

5. Create default users:
   ```
   python manage.py seed_users
   ```

6. (Optional) Seed dummy data for testing:
   ```
   python manage.py seed_dummy_data
   ```

7. Run the development server:
   ```
   python manage.py runserver
   ```

8. Access the application at http://127.0.0.1:8000/

## Default Users

The system comes with three default user accounts:

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Administrator |
| manager1 | manager123 | Case Manager |
| officer1 | officer123 | Field Officer |

## Dummy Data

The `seed_dummy_data` command creates the following test data:

### Categories
- Category 1 (max annual amount: 500,000)
- Category 2 (max annual amount: 750,000)
- Category 3 (max annual amount: 1,000,000)

### Programs
- Girinka (One Cow per Poor Family Program, monthly amount: 50,000)
- VUP (Vision 2020 Umurenge Program, monthly amount: 30,000)
- Twiyubake (Self-reliance and economic empowerment program, monthly amount: 40,000)

### Beneficiaries
- Between 20-30 randomly generated beneficiaries
- Distributed across the three categories and programs
- With random names, ages, genders, and addresses

## User Roles and Permissions

### Administrator
- Full access to all system features
- User management
- Configuration settings
- Reports and analytics
- All CRUD operations on all entities

### Case Manager
- Manage beneficiaries
- Create and manage cases
- Assign assessments
- View and edit case notes
- Limited administrative functions

### Field Officer
- View assigned beneficiaries
- Record assessment data
- Add case notes
- View limited case information

## API Documentation

The system provides a comprehensive RESTful API:

- API Root: `/api/`
- Swagger Documentation: `/swagger/`
- ReDoc Documentation: `/redoc/`

### Available Endpoints

- `/api/users/` - User management
- `/api/beneficiaries/` - Beneficiary management
- `/api/cases/` - Case management
- `/api/case-notes/` - Case notes
- `/api/assessments/` - Assessments
- `/api/assessment-questions/` - Assessment questions
- `/api/assessment-answers/` - Assessment answers

## Project Structure

```
aidconnect/
├── aidconnect/            # Project settings and main URL configuration
├── core/                  # Main application
│   ├── management/        # Custom management commands
│   │   └── commands/      
│   │       ├── seed_users.py      # Command to create default users
│   │       └── seed_dummy_data.py # Command to seed dummy data for testing
│   ├── migrations/        # Database migrations
│   ├── models.py          # Data models
│   ├── serializers.py     # API serializers
│   ├── views.py           # Views and viewsets
│   ├── urls.py            # URL routing
│   └── admin.py           # Admin site configuration
├── templates/             # HTML templates
│   ├── base.html          # Base template with common layout
│   ├── login.html         # Login page
│   ├── dashboard/         # Dashboard templates
│   └── beneficiaries/     # Beneficiary management templates
└── manage.py              # Django management script
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For support, please open an issue in the GitHub repository or contact the project maintainers.
