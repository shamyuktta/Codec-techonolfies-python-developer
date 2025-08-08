import os, uuid
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
import bcrypt, jwt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///auth.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
ACCESS_EXP_MIN = int(os.getenv("ACCESS_EXPIRES_MINUTES", "15"))
REFRESH_EXP_DAYS = int(os.getenv("REFRESH_EXPIRES_DAYS", "30"))
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.LargeBinary(60), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RefreshToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    revoked = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    replaced_by = db.Column(db.String(36), nullable=True)

def hash_password(p): return bcrypt.hashpw(p.encode(), bcrypt.gensalt(BCRYPT_ROUNDS))
def verify_password(p, h): return bcrypt.checkpw(p.encode(), h)

def create_token(user_id, typ="access"):
    now = datetime.utcnow()
    jti = str(uuid.uuid4())
    exp = now + (timedelta(minutes=ACCESS_EXP_MIN) if typ=="access" else timedelta(days=REFRESH_EXP_DAYS))
    payload = {"sub":str(user_id),"iat":now,"exp":exp,"jti":jti,"typ":typ}
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token, payload

@app.before_first_request
def create_tables():
    db.create_all()

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email, pwd = data.get("email","").lower().strip(), data.get("password","")
    if not email or not pwd: return {"msg":"missing"},400
    if User.query.filter_by(email=email).first(): return {"msg":"exists"},409
    u = User(email=email, password_hash=hash_password(pwd))
    db.session.add(u); db.session.commit()
    return {"msg":"ok"},201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email, pwd = data.get("email","").lower().strip(), data.get("password","")
    u = User.query.filter_by(email=email).first()
    if not u or not verify_password(pwd, u.password_hash): return {"msg":"bad creds"},401
    access_token, _ = create_token(u.id, "access")
    refresh_token, rl_payload = create_token(u.id, "refresh")
    rt = RefreshToken(jti=rl_payload["jti"], user_id=u.id, expires_at=rl_payload["exp"])
    db.session.add(rt); db.session.commit()
    resp = jsonify(access_token=access_token)
    resp.set_cookie("refresh_token", refresh_token, httponly=True, secure=False, samesite="Strict", max_age=60*60*24*REFRESH_EXP_DAYS)
    return resp

from functools import wraps
def jwt_required(f):
    @wraps(f)
    def w(*a, **k):
        auth = request.headers.get("Authorization","")
        if not auth.startswith("Bearer "): return {"msg":"no token"},401
        token = auth.split(None,1)[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            if payload.get("typ")!="access": raise jwt.InvalidTokenError()
        except jwt.ExpiredSignatureError: return {"msg":"expired"},401
        except jwt.InvalidTokenError: return {"msg":"invalid"},401
        g.current_user = User.query.get(int(payload["sub"]))
        return f(*a, **k)
    return w

@app.route("/me")
@jwt_required
def me():
    u = g.current_user
    return {"id":u.id,"email":u.email}

@app.route("/refresh", methods=["POST"])
def refresh():
    token = request.cookies.get("refresh_token")
    if not token: return {"msg":"no refresh"},401
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        if payload.get("typ")!="refresh": raise jwt.InvalidTokenError()
    except jwt.ExpiredSignatureError: return {"msg":"refresh expired"},401
    except jwt.InvalidTokenError: return {"msg":"invalid"},401
    rt = RefreshToken.query.filter_by(jti=payload["jti"]).first()
    if not rt or rt.revoked: return {"msg":"revoked"},401
    rt.revoked=True
    new_token, new_payload = create_token(rt.user_id, "refresh")
    new_rt = RefreshToken(jti=new_payload["jti"], user_id=rt.user_id, expires_at=new_payload["exp"])
    db.session.add(new_rt); db.session.commit()
    access_token, _ = create_token(rt.user_id, "access")
    resp = jsonify(access_token=access_token)
    resp.set_cookie("refresh_token", new_token, httponly=True, secure=False, samesite="Strict", max_age=60*60*24*REFRESH_EXP_DAYS)
    return resp

@app.route("/logout", methods=["POST"])
def logout():
    token = request.cookies.get("refresh_token")
    if token:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            rt = RefreshToken.query.filter_by(jti=payload["jti"]).first()
            if rt:
                rt.revoked=True
                db.session.commit()
        except Exception:
            pass
    resp = jsonify({"msg":"bye"})
    resp.set_cookie("refresh_token","",expires=0)
    return resp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
