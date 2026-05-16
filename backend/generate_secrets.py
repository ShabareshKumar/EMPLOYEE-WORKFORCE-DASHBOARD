#!/usr/bin/env python3
"""
Generate secure random keys for production deployment
Usage: python generate_secrets.py
"""
import secrets

print("=" * 70)
print("SECURE KEY GENERATOR FOR PRODUCTION")
print("=" * 70)
print()
print("Copy these values to your backend/.env file:")
print()
print("-" * 70)
print(f"SECRET_KEY={secrets.token_hex(32)}")
print(f"JWT_SECRET_KEY={secrets.token_hex(32)}")
print("-" * 70)
print()
print("⚠️  IMPORTANT:")
print("  1. Keep these keys secret")
print("  2. Never commit them to version control")
print("  3. Use different keys for each environment (dev, staging, prod)")
print("  4. Store them securely in your deployment platform")
print()
print("=" * 70)
