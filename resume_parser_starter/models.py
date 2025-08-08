from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
db = SQLAlchemy()

class Candidate(db.Model):
    __tablename__ = "candidate"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True)
    email = db.Column(db.String, index=True)
    phone = db.Column(db.String, index=True)
    skills = db.Column(JSONB)
    education = db.Column(JSONB)
    experience = db.Column(JSONB)
    resume_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

def init_db():
    db.create_all()
