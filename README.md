# Codec-techonolfies-python-developer
# 🔐 Secure Authentication System – Flask + JWT

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Flask](https://img.shields.io/badge/Flask-2.3-green)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

A secure login & registration system with **JWT authentication** and **password hashing**.

## 🚀 Features
- User registration with `bcrypt` password hashing
- JWT-based authentication (`access` + `refresh` tokens)
- PostgreSQL integration
- Secure session cookies (HTTP-only)
- RESTful endpoints

## 🛠 Tech Stack
- Python (Flask)
- PostgreSQL
- PyJWT
- bcrypt

## 📦 Setup

```bash
git clone https://github.com/YOUR_USERNAME/secure-auth-flask-jwt.git
cd secure-auth-flask-jwt
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
flask run
