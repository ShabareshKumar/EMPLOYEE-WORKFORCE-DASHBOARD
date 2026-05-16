# Frontend - Workforce Analytics Dashboard

React-based frontend for the Workforce Analytics Dashboard.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

Application runs on `http://localhost:3000`

## Build for Production

```bash
npm run build
```

## Project Structure

```
src/
├── components/       # Reusable components
│   ├── Layout.jsx
│   ├── Sidebar.jsx
│   ├── Navbar.jsx
│   ├── StatCard.jsx
│   ├── Alert.jsx
│   ├── Modal.jsx
│   ├── Loader.jsx
│   └── ProtectedRoute.jsx
├── pages/           # Page components
│   ├── Login.jsx
│   ├── Dashboard.jsx
│   ├── Timesheets.jsx
│   ├── Analytics.jsx
│   ├── AdminPanel.jsx
│   └── Profile.jsx
├── context/         # Context providers
│   └── AuthContext.jsx
├── api/             # API configuration
│   └── axios.js
├── App.jsx          # Main app component
├── main.jsx         # Entry point
└── index.css        # Global styles
```

## Features

- Modern SaaS UI with Tailwind CSS
- Responsive design (mobile + desktop)
- Interactive charts with Chart.js
- JWT authentication
- Role-based routing
- Context API for state management

## Environment Variables

Update API URL in `src/api/axios.js`:

```javascript
const api = axios.create({
  baseURL: 'http://localhost:5000/api'  // Change for production
})
```

## Deployment

Deploy to Vercel:

```bash
npm i -g vercel
vercel
```

Or deploy to Netlify:

```bash
npm run build
# Upload dist/ folder to Netlify
```
