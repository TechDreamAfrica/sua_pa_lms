# Smart Campus System - University of Central Technology (UCT)

A comprehensive Django-based digital transformation platform for University of Central Technology, featuring a Learning Management System (LMS), student services portal, and administration dashboard.

## 🚀 Features

### Learning Management System (LMS)

- **Course Management**: Create, manage, and enroll in courses
- **Assignment System**: Submit and grade assignments with file uploads
- **Quiz Engine**: Create and take quizzes with multiple question types
- **Module Structure**: Organize course content into modules and lessons
- **Grade Tracking**: Monitor student progress and grades

### Student Services Portal

- **Digital ID**: QR-coded digital student identification
- **Timetable Management**: View personalized class schedules
- **Academic Records**: Access transcripts and grades
- **Event Management**: Browse and register for campus events
- **Library System**: Search and borrow library resources
- **Notifications**: Receive important announcements and updates

### Administration Dashboard

- **User Management**: Manage students, faculty, and staff accounts
- **Course Administration**: Create and manage academic programs
- **Department Management**: Organize university structure
- **Room Booking**: Schedule and manage campus facilities
- **Attendance Tracking**: Monitor student attendance
- **Reports**: Generate academic and administrative reports
- **Maintenance System**: Track and manage campus maintenance requests
- **Announcements**: Broadcast important information

## 🛠️ Technology Stack

- **Backend**: Django 5.2.4 (Python)
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **Database**: SQLite (development) / PostgreSQL (production)
- **Forms**: Django Crispy Forms with Tailwind styling
- **Authentication**: Django's built-in auth system
- **File Handling**: Django's file upload system
- **Icons**: Font Awesome 6.4.0

## 📦 Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd smart-campus
   ```

2. **Create virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install django pillow django-crispy-forms crispy-tailwind
   ```

4. **Run migrations**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**

   ```bash
   python manage.py createsuperuser
   ```

6. **Create sample data** (optional)

   ```bash
   python create_users.py
   ```

7. **Run development server**

   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## 👥 Default Users

The system comes with pre-configured user accounts:

- **Admin**: username: `admin`, password: `admin123`
- **Student**: username: `student1`, password: `student123`
- **Faculty**: username: `faculty1`, password: `faculty123`

## 📱 Responsive Design

The platform is fully responsive and works seamlessly across:

- Desktop computers
- Tablets
- Mobile phones

## 🎨 UI/UX Features

- **Modern Interface**: Clean, professional design with UCT branding
- **Intuitive Navigation**: Easy-to-use menus and breadcrumbs
- **Interactive Elements**: Hover effects and smooth transitions
- **Accessibility**: WCAG compliant design principles
- **Dark Mode Ready**: Prepared for future dark theme implementation

## 🔧 Project Structure

```
smart_campus/
├── accounts/           # User authentication and profiles
├── lms/               # Learning Management System
├── student_services/  # Student portal services
├── administration/    # Admin dashboard and management
├── templates/         # HTML templates
├── static/           # CSS, JavaScript, images
├── media/            # User uploaded files
└── smart_campus/     # Project settings
```

## 🔐 Security Features

- CSRF protection on all forms
- User authentication and authorization
- Permission-based access control
- Secure file upload handling
- SQL injection prevention
- XSS protection

## 🌟 Key Highlights

- **Scalable Architecture**: Modular Django app structure
- **Modern UI**: Tailwind CSS for responsive design
- **User-Friendly**: Intuitive interface for all user types
- **Comprehensive**: Covers all major university operations
- **Extensible**: Easy to add new features and modules
- **Mobile-First**: Optimized for mobile usage

## 📈 Future Enhancements

- Real-time chat and messaging
- Video conferencing integration
- Mobile application (React Native)
- API development for third-party integrations
- Advanced analytics and reporting
- Payment gateway integration
- Multi-language support

## 🤝 Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏫 About UCT

University of Central Technology (UCT) is a mid-sized institution committed to providing innovative education through technology integration and modern teaching methodologies.

## 📞 Support

For technical support or questions, please contact:

- Email: support@uct.edu
- Phone: +1 (555) 123-4567

---

**Smart Campus System** - Empowering education through technology 🎓
