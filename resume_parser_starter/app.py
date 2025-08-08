import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from parser_module import parse_resume, extract_text
from models import db, Candidate, init_db
from config import get_database_uri

UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db.init_app(app)
with app.app_context():
    init_db()

@app.route("/health", methods=["GET"])
def health():
    return {"status":"ok"}, 200

@app.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    if not f:
        return {"error":"no file provided"}, 400
    filename = secure_filename(f.filename)
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    f.save(path)
    parsed = parse_resume(path)
    # Save to DB
    candidate = Candidate(
        name=parsed.get("name"),
        email=parsed.get("email"),
        phone=parsed.get("phone"),
        skills=parsed.get("skills"),
        education=parsed.get("education"),
        experience=parsed.get("experience"),
        resume_text=parsed.get("text")
    )
    db.session.add(candidate)
    db.session.commit()
    return jsonify({"id": candidate.id, "parsed": parsed}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
