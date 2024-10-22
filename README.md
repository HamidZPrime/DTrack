
# DTrack

**DTrack** is a comprehensive platform designed to manage and monitor product data integrity with a focus on food safety, supplier certifications, sustainability, and automation. It digitizes supplier certificates and integrates automated workflows to enhance sustainability and compliance processes.

## Key Features

- **Digitized Supplier Certificates**: Centralized storage and management of all supplier certificates with integrity checks and versioning.
- **Role-based User Management**: Four user types with varying levels of access: Admins, Suppliers, Normal Users, and Operators.
- **Supplier Panel**: Dedicated panel for suppliers to manage their data, products, and certifications.
- **Sustainability Compliance**: Track and enforce sustainability standards by managing and monitoring certificates related to sustainability efforts.
- **Certificate Integrity Checks**: Detection and flagging of potentially tampered files (JPG, PNG, PDF).
- **Automation and Notifications**: Automated workflows and email notifications based on certificate expiry or compliance criteria.
- **Multi-language Support**: Currently supports English and Arabic.
- **Email Verification**: Email-based account verification and token management.
- **Profile Completion Workflow**: Mandatory profile completion and admin/operator review for account activation.
- **QR Code Scanning for Users**: End users can scan QR codes to access product and supplier details.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Project Structure](#project-structure)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Available Apps](#available-apps)
6. [License](#license)

## Getting Started

### Prerequisites

- **Python 3.8+**
- **Django 4.x**
- **PostgreSQL**
- **Django Templates** (No DRF or API reliance)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/DTrack.git
   ```
2. Navigate to the project directory:
   ```bash
   cd DTrack
   ```
3. Create a virtual environment and activate it:
   ```bash
   python3 -m venv env
   source env/bin/activate
   ```
4. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Set up your database and migrate:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Create a superuser for administrative access:
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

```plaintext
DTrack/
├── accounts/             # Manages users and roles
├── analytics/            # Advanced analytics for user and certificate insights
├── approvals/            # Approval workflow for profiles and certifications
├── audit_logs/           # Auditing actions within the system
├── certificates/         # Handles certificates and integrity checks
├── compliance/           # Manages compliance standards and sustainability efforts
├── dashboard/            # User-friendly dashboards for various roles
├── dtrack/               # Core Django project settings
├── file_management/      # File management and secure storage
├── food_safety/          # Modules dedicated to food safety compliance
├── inventory/            # Inventory management and tracking
├── locale/               # Multi-language support files
├── notifications/        # Automated notifications and alerts
├── payments/             # Payment-related management
├── profiles/             # Manages additional user details and profiles
├── qr_generator/         # Generates and manages QR codes
├── reports/              # Reporting module for insights
├── supplier_management/  # Dedicated supplier management
├── support/              # Customer support and issue management
├── system_settings/      # System configurations and settings
├── task_scheduler/       # Automated task and notification scheduling
├── templates/            # Custom Django templates
├── static/               # Static files
├── media/                # Uploaded media
├── manage.py             # Django’s command-line utility
└── README.md             # This file
```

## Available Apps

1. **accounts**: User authentication and management with different roles (admin, supplier, end user, operator).
2. **certificates**: Upload and integrity check for certificates with tampering detection.
3. **compliance**: Handles sustainability standards and compliance management.
4. **profile**: Extended user information and profile completion.
5. **task_scheduler**: Logic and conditions for automated notifications and tasks.
6. **qr_generator**: Generates and manages QR codes linked to products.

## Usage

- **Admin Panel**: Full access to manage users, certificates, compliance, and system configurations.
- **Supplier Panel**: Manage product data, certificates, and sustainability compliance.
- **QR Code Scanning**: Normal users can scan codes to view relevant product and supplier details.
- **Automated Workflows**: Notifications and tasks based on expiry and compliance.

## License

**DTrack** is a commercial software product and all rights are owned by **Z Prime LTD**. Redistribution or commercial use without permission is strictly prohibited.

---
