# Workforce Analytics

A full-stack workforce productivity analytics application built with **React + Flask + PostgreSQL**.

## Features

- **JWT Authentication** — Secure login with role-based access control (Admin, Manager, Employee)
- **Timesheet Management** — Log productive and non-productive hours per project and task
- **Project Management** — Create projects manually or by uploading Excel files (.xlsx, .xls, .csv)
- **Local AI Analysis** — Excel files are analyzed locally with no external API calls
- **Analytics Dashboard** — KPIs, productivity scores, weekly trends, and employee performance charts
- **Demo Account** — Read-only demo access for recruiters and reviewers
- **Rate Limiting** — Brute-force protection on login (5 attempts/minute)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite 5, Tailwind CSS, Chart.js |
| Backend | Flask 3, SQLAlchemy, PyJWT, Flask-Limiter |
| Database | PostgreSQL (production), SQLite (local dev) |
| Hosting | Vercel (frontend) + Render (backend) |

## Project Structure

```
workforce-analytics/
├── backend/
│   ├── app.py              # Flask app factory
│   ├── config.py           # Environment-based configuration
│   ├── requirements.txt    # Python dependencies
│   ├── create_admin.py     # CLI script to create admin user
│   ├── models/             # SQLAlchemy models
│   ├── routes/             # API blueprints
│   └── utils/              # Auth, validators, rate limiting
├── frontend/
│   ├── src/
│   │   ├── api/            # Axios instance with JWT interceptor
│   │   ├── components/     # Reusable UI components
│   │   ├── context/        # Auth context
│   │   └── pages/          # Route pages
│   └── vite.config.js
├── render.yaml             # Render backend deployment config
├── vercel.json             # Vercel frontend deployment config
└── README.md
```

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your local values

python app.py
```

### Frontend Setup

```bash
cd frontend
npm install

# Copy and configure environment variables
cp .env.example .env.local
# Set VITE_API_URL=http://localhost:5000/api

npm run dev
```

## Environment Variables

### Backend (`backend/.env`)

```env
DATABASE_URL=sqlite:///database.db     # Use PostgreSQL URL in production
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
DEBUG=True                             # Set to False in production
ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend (`frontend/.env.production`)

```env
VITE_API_URL=https://your-backend.onrender.com/api
```

## Production Deployment

### Backend → Render

1. Create a PostgreSQL database on Render
2. Create a Web Service connected to this repository
3. Set environment variables in the Render dashboard:
   - `DATABASE_URL` — from PostgreSQL addon
   - `SECRET_KEY` — auto-generated
   - `JWT_SECRET_KEY` — auto-generated
   - `DEBUG=False`
   - `ALLOWED_ORIGINS` — your Vercel URL
4. After deploy, create admin user via Render Shell:
   ```bash
   cd backend && python create_admin.py
   ```

### Frontend → Vercel

1. Import repository on Vercel
2. Set Root Directory to `frontend`
3. Add environment variable: `VITE_API_URL=https://your-backend.onrender.com/api`
4. Deploy

## Demo Account

| Field | Value |
|-------|-------|
| Email | `demo@demo.com` |
| Password | `Demo123` |
| Access | Read-only |

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/login` | ❌ | Login |
| POST | `/api/register` | ❌ | Register |
| GET | `/api/profile` | ✅ | Current user |
| GET/POST | `/api/users` | ✅ Admin | User management |
| GET/POST | `/api/projects` | ✅ | Projects |
| POST | `/api/projects/upload` | ✅ Manager | Excel upload |
| GET/POST | `/api/timesheets` | ✅ | Timesheets |
| GET | `/api/analytics` | ✅ Manager | Analytics |
| GET | `/health` | ❌ | Health check |

## Security

- JWT tokens expire after 1 hour
- Passwords hashed with PBKDF2 (werkzeug)
- Rate limiting on login endpoint
- CORS restricted to configured origins in production
- File uploads validated (type, size, filename sanitization)
- All text inputs sanitized with bleach
