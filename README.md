# Recycling Tracker 🌍♻️

A comprehensive Django-based web application for managing recycling requests, centers, and user interactions. This platform connects users with recycling centers, facilitates request management, and tracks environmental impact.

## 🚀 Features

### User Roles
- **Normal Users**: Submit recycling requests, track requests, find nearby centers
- **Admin Users**: Manage users, create/manage recycling centers, assign staff
- **Staff Users**: Approve/reject requests, manage assigned centers

### Core Functionality
- 🗺️ **Interactive Map View**: Find recycling centers with geolocation
- 📋 **Request Management**: Create, track, and manage recycling requests
- 🔔 **Real-time Notifications**: In-app and email notifications
- 📊 **Dashboard Analytics**: Track recycling statistics and environmental impact
- 👥 **User Management**: Role-based access control
- 🏢 **Center Management**: Admin tools to manage recycling facilities

## 🛠️ Tech Stack

- **Backend**: Django 5.2.6
- **Database**: SQLite (Development)
- **Frontend**: Bootstrap 5, JavaScript
- **Python**: 3.13.1

## 📦 Installation

### Prerequisites
- Python 3.13+
- pip
- Git

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Om15042002/Recyling-Tracker.git
   cd Recyling-Tracker
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Load sample data (Optional)**
   ```bash
   python manage.py load_sample_data
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Open browser: `http://127.0.0.1:8000/`
   - Admin panel: `http://127.0.0.1:8000/admin/`

## 📂 Project Structure

```
recycling_tracker/
├── accounts/              # User authentication and profiles
├── recycling_centers/     # Recycling center management
├── recycling_requests/    # Request handling
├── notifications/         # Notification system
├── templates/            # HTML templates
├── static/               # CSS, JS, images
├── media/                # User uploaded files
├── manage.py            # Django management script
└── recycling_tracker/   # Project settings
```

## 👤 User Types

### Normal User Features
- Register and login
- Submit recycling requests
- Track request status
- Find nearby recycling centers
- View recycling history and statistics

### Admin Features
- All normal user features
- Manage all users
- Create and manage recycling centers
- Assign staff to centers
- View system-wide statistics

### Staff Features
- Approve/reject recycling requests
- Manage assigned centers
- View pending requests
- Add notes to requests

## 🌟 Key Features Explained

### Request Management
Users can submit requests with:
- Material type (plastic, paper, glass, metal, electronics, etc.)
- Quantity and estimated weight
- Pickup address and preferred date
- Item images
- Priority levels

### Recycling Centers
- Location with GPS coordinates
- Accepted materials
- Operating hours
- Capacity tracking
- Staff assignments

### Notifications
- Request status updates
- Approval/rejection notifications
- Email integration support
- Real-time unread count

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:
```
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database
Currently using SQLite for development. For production, configure PostgreSQL in `settings.py`.

## 🧪 Testing

Run tests:
```bash
python manage.py test
```

## 📝 Management Commands

### Load Sample Data
```bash
python manage.py load_sample_data
```

### Create Test Users
```bash
python create_test_users.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is part of an academic course: Internet Applications and Distributed Systems

## 👨‍💻 Author

**Om Siddhapura**
- GitHub: [@Om15042002](https://github.com/Om15042002)

## 🙏 Acknowledgments

- Django documentation
- Bootstrap framework
- FontAwesome icons

## 📞 Support

For support, please open an issue in the GitHub repository.

---
**Course**: Internet Applications and Distributed Systems  
**Semester**: 3  
**Year**: 2025
