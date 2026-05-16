# Backend - Workforce Analytics API

Flask-based REST API for the Workforce Analytics Dashboard.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Run application:
```bash
python app.py
```

Server runs on `http://localhost:5000`

## Database

SQLite database is automatically created on first run with a default admin user:
- Email: admin@company.com
- Password: admin123

## API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/register` - User registration

### Timesheets
- `GET /api/timesheets` - Get timesheets
- `POST /api/timesheets` - Create timesheet
- `PUT /api/timesheets/:id` - Update timesheet
- `DELETE /api/timesheets/:id` - Delete timesheet

### Analytics
- `GET /api/analytics` - Get analytics data
- `GET /api/analytics/employee/:id` - Get employee analytics

### Users
- `GET /api/users` - Get all users (admin/manager)
- `POST /api/users` - Create user (admin)
- `PUT /api/users/:id` - Update user (admin)
- `DELETE /api/users/:id` - Delete user (admin)

### Profile
- `GET /api/profile` - Get current user profile

## Environment Variables

```
DATABASE_URL=sqlite:///database.db
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DEBUG=True
```

## Production Deployment

For production, use PostgreSQL:

```bash
pip install psycopg2-binary
```

Update `.env`:
```
DATABASE_URL=postgresql://user:password@host:port/database
DEBUG=False
```
