# LeaveEase – Smart Leave Management Portal 🏫

LeaveEase is a Django-based web application designed to simplify and digitize leave management for **students, faculty, and administrators**.  
It provides role-based dashboards, real-time leave tracking, and automated balance management.

---

## 🚀 Features

### 🔑 Authentication & Security
- User registration with role selection (Student, Faculty, Admin).
- Secure login with email & password.
- Role-based dashboard redirection after login.
- Logout functionality.

### 👨‍🎓 Student Features
- Apply for different types of leaves:
  - Casual Leave
  - Medical Leave
  - Emergency Leave
  - Academic Leave
- Upload documents (e.g., medical certificate) when applying.
- View applied leaves and their statuses (Pending, Approved, Rejected).
- Check remaining leave balances for each leave type.
- Dashboard with leave statistics.

### 👩‍🏫 Faculty Features
- Department-specific leave request view.
- Tabs to filter requests (Pending / All).
- Approve or Reject student leave requests.
- See quick stats: Pending, Approved, Rejected requests count.
- Manage leave balances automatically when approving.

### 🛠 Admin Features
- Dashboard with system-wide analytics:
  - Total users
  - Total leave requests
  - Pending requests
  - Approval rate %
- Visual charts:
  - Monthly leave request trends
  - Leave type distribution
- Manage users (Students, Faculty).
- Department-level statistics.

### 📊 Analytics
- Charts for monthly leave requests.
- Pie/Bar charts for leave type distribution.
- Department-wise request tracking.

---

## 🛠️ Tech Stack
- **Backend:** Django, Python
- **Frontend:** HTML, Tailwind CSS
- **Database:** SQLite (default) – can switch to PostgreSQL/MySQL
- **Authentication:** Django Auth with role-based access

---

## 📦 Project Setup

### 1️⃣ Clone the Repository
git clone https://github.com/praneesha17/LeaveEase.git
cd LeaveEase
### 2️⃣ Create Virtual Environment
python -m venv env
source env/bin/activate   # On Linux/Mac
env\Scripts\activate      # On Windows
### 3️⃣ Install Dependencies
pip install -r requirements.txt
### 4️⃣ Run Migrations
python manage.py makemigrations
python manage.py migrate
### 5️⃣ Run Development Server
python manage.py runserver

## 📊 Roles & Dashboards
Student Dashboard: Apply & track leaves, view balances.
Faculty Dashboard: Approve/Reject leave requests, track departmental stats.
Admin Dashboard: View analytics, manage system-wide stats & users.
