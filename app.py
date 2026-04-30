from flask import Flask,request
from models import db,User,APILog,Project
from flask_jwt_extended import JWTManager, create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import CORS
import bcrypt
from collections import Counter
import uuid

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY']='supersecret'

CORS(app)
jwt = JWTManager(app)
db.init_app(app)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    existing = User.query.filter_by(username=username).first()
    if existing:
        return {"message": "User already exists"}, 400
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = User(username=username, password=hashed.decode('utf-8'))
    db.session.add(user)
    db.session.commit()

    return {"message": "User registered successfully"}

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    if not user:
        return {"message": "Invalid credentials"}, 401

    if not bcrypt.checkpw(data.get('password').encode('utf-8'), user.password.encode('utf-8')):
        return {"message": "Invalid credentials"}, 401

    access_token = create_access_token(identity=str(user.id))
    return {"token": access_token}

@app.route('/profile',methods=['GET'])
@jwt_required()
def profile():
    user_id = int(get_jwt_identity())
    return {"message": f"welcome user {user_id}"}

@app.route('/log', methods=['POST'])
def log_api():
    data = request.json
    api_key = data.get('api_key')
    endpoint = data.get('endpoint')
    response_time = data.get('response_time')
    status = data.get('status')
    project = Project.query.filter_by(api_key=api_key).first()

    if not project:
        return {"message": "Invalid API key"}, 401
    new_log = APILog(
        endpoint=endpoint,
        response_time=response_time,
        status=status,
        project_id=project.id
    )
    db.session.add(new_log)
    db.session.commit()
    return {"message": "Log stored successfully"}

@app.route('/create_project', methods=['POST'])
@jwt_required()
def create_project():
    data = request.json
    name = data.get('name')
    user_id = int(get_jwt_identity())
    existing = Project.query.filter_by(name=name, user_id=user_id).first()
    if existing:
        return {"message": "Project with this name already exists"}, 400
    api_key = str(uuid.uuid4())
    project = Project(
        name=name,
        api_key=api_key,
        user_id=user_id
    )
    db.session.add(project)
    db.session.commit()
    sample_logs = [
        APILog(endpoint="/login", response_time=120, status=200, project_id=project.id),
        APILog(endpoint="/dashboard", response_time=180, status=200, project_id=project.id),
        APILog(endpoint="/products", response_time=250, status=500, project_id=project.id),
    ]
    db.session.add_all(sample_logs)
    db.session.commit()

    return {
        "message": "Project created",
        "api_key": api_key,
        "project_id": project.id
    }

@app.route('/project_analytics/<int:project_id>', methods=['GET'])
@jwt_required()
def project_analytics(project_id):
    user_id = int(get_jwt_identity())
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return {"message": "Project not found"}, 404
    logs = APILog.query.filter_by(project_id=project_id).all()
    total_requests = len(logs)
    error_count = sum(1 for log in logs if log.status and log.status >= 400)
    error_rate = (error_count / total_requests * 100) if total_requests else 0
    avg_response_time = (
        sum(log.response_time for log in logs if log.response_time) / total_requests
        if total_requests else 0
    )
    endpoint_counts = Counter(log.endpoint for log in logs)

    top_endpoints = [
        {"endpoint": ep, "count": count}
        for ep, count in endpoint_counts.most_common(5)
    ]
    return {
        "project": project.name,
        "total_requests": total_requests,
        "error_rate": round(error_rate, 2),
        "avg_response_time": round(avg_response_time, 2),
        "top_endpoints": top_endpoints
    }

@app.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    user_id = int(get_jwt_identity())
    projects = Project.query.filter_by(user_id=user_id).all()
    result = []
    for p in projects:
        result.append({
            "id": p.id,
            "name": p.name,
            "api_key": p.api_key
        })
    return {"projects": result}

@app.route('/update_project/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    user_id = int(get_jwt_identity())
    data = request.json
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return {"message": "Project not found"}, 404
    project.name = data.get('name', project.name)
    db.session.commit()
    return {"message": "Project updated successfully"}

@app.route('/delete_project/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_project(id):
    user_id = int(get_jwt_identity())
    project = Project.query.filter_by(id=id, user_id=user_id).first()
    if not project:
        return {"message": "Project not found"}, 404
    APILog.query.filter_by(project_id=id).delete()
    db.session.delete(project)
    db.session.commit()
    return {"message": "Project deleted"}

@app.route('/analytics',methods=['GET'])
@jwt_required()
def analytics():
    user_id=int(get_jwt_identity())
    logs = APILog.query.join(Project).filter(Project.user_id == user_id).all()
    total_requests=len(logs)
    error_count = sum(1 for log in logs if log.status and log.status >= 400)
    error_rate=(error_count/total_requests * 100) if total_requests > 0 else 0
    avg_response_time= (
        sum(log.response_time for log in logs if log.response_time)/total_requests
        if total_requests > 0 else 0
    )

    return {
    "total_requests": total_requests,
    "error_rate": round(error_rate, 2),
    "avg_response_time": round(avg_response_time, 2)
    }


@app.route('/')
def home():
    return{"message":"Devtrack Running"}

if __name__=="__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)