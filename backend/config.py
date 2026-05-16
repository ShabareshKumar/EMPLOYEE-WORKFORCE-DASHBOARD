import os
import secrets
from datetime import timedelta
from dotenv import load_dotenv

# Load .env FIRST (only applies locally - Render uses dashboard env vars)
load_dotenv()

def _get_debug():
    return os.getenv('DEBUG', 'False').strip().lower() in ('true', '1', 'yes')

class Config:
    # ── Mode ──────────────────────────────────────────────────────────────────
    DEBUG = _get_debug()

    # ── Database ──────────────────────────────────────────────────────────────
    _db_url = os.getenv('DATABASE_URL')
    if not _db_url:
        if DEBUG:
            _db_url = 'sqlite:///database.db'  # local dev fallback only
        else:
            raise RuntimeError("DATABASE_URL environment variable is not set!")

    # Render uses postgres:// — SQLAlchemy requires postgresql://
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 20,
        'pool_timeout': 30,
        'echo': False
    }

    # ── Secrets ───────────────────────────────────────────────────────────────
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # ── File Upload ───────────────────────────────────────────────────────────
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

    # ── Security ──────────────────────────────────────────────────────────────
    SESSION_COOKIE_SECURE = not DEBUG   # HTTPS only in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    WTF_CSRF_CHECK_DEFAULT = False

    @staticmethod
    def init_app():
        """Validate all required config at startup — fails fast if misconfigured."""
        is_debug = _get_debug()

        # ── Production guards ─────────────────────────────────────────────────
        if not is_debug:
            # Re-check DATABASE_URL at runtime (catches missing var even if class
            # body was evaluated before env was fully set)
            db_url = os.getenv('DATABASE_URL', '')
            if not db_url:
                raise RuntimeError("DATABASE_URL environment variable is not set!")
            if 'localhost' in db_url or '127.0.0.1' in db_url:
                raise RuntimeError("DATABASE_URL points to localhost — use PostgreSQL in production!")
            if not db_url.startswith(('postgresql://', 'postgres://')):
                raise RuntimeError(f"DATABASE_URL must be a PostgreSQL URL, got: {db_url[:20]}...")

        # ── Secret key validation ─────────────────────────────────────────────
        if not Config.SECRET_KEY:
            if is_debug:
                Config.SECRET_KEY = 'dev-secret-' + secrets.token_hex(32)
                print("⚠️  WARNING: Using auto-generated SECRET_KEY (development only)")
            else:
                raise RuntimeError("SECRET_KEY environment variable is not set!")

        if not Config.JWT_SECRET_KEY:
            if is_debug:
                Config.JWT_SECRET_KEY = 'dev-jwt-' + secrets.token_hex(32)
                print("⚠️  WARNING: Using auto-generated JWT_SECRET_KEY (development only)")
            else:
                raise RuntimeError("JWT_SECRET_KEY environment variable is not set!")

        # Reject known placeholder values
        _bad_keys = [
            'your-secret-key-change-in-production',
            'your-secret-key-here',
            'changeme',
            'secret',
        ]
        if Config.SECRET_KEY in _bad_keys:
            raise RuntimeError("SECRET_KEY is a placeholder — set a real secret!")
        if Config.JWT_SECRET_KEY in _bad_keys:
            raise RuntimeError("JWT_SECRET_KEY is a placeholder — set a real secret!")

        return True
