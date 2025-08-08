# Flask JWT Auth Example

Minimal Flask app demonstrating secure authentication with:
- bcrypt password hashing
- JWT access & refresh tokens
- Refresh token rotation & revocation stored in DB (RefreshToken table)
- SQLite default for easy local testing; use Postgres in production via DATABASE_URL

## Quick start
1. Create virtualenv and install:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. (Optional) Copy `.env.example` to `.env` and edit.
3. Run:
   ```bash
   python app.py
   ```
4. Endpoints:
   - POST /register  { "email":"you@example.com", "password":"secret" }
   - POST /login     { "email":"you@example.com", "password":"secret" } => sets refresh cookie and returns access token
   - POST /refresh    (uses HttpOnly cookie) => rotates refresh token, returns new access token
   - POST /logout     (uses cookie) => revokes refresh token
   - GET  /me         (requires Authorization: Bearer <access_token>)

## Notes
- This is an educational template. Do **not** use as-is in production.
- Ensure HTTPS, use secure cookies, use stronger secret management, add rate limiting, monitoring and tests.
