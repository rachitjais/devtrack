from flask import Flask,request
from models import db,User,APILog
from flask_jwt_extended import JWTManager, create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY']='supersecret'

jwt = JWTManager(app)
db.init_app(app)

@app.route('/register',methods=['POST'])
def register():
    data=request.json
    username=data.get('username')
    password=data.get('password')

    new_user=User(username=username,password=password)

    db.session.add(new_user)
    db.session.commit()

    return{"message":"User registered successfully"}

@app.route('/login',methods=['POST'])
def login():
    data= request.json
    username=data.get('username')
    password=data.get('password')

    user=User.query.filter_by(username=username).first()

    if not user or user.password != password:
        return {"message":"Invalid credentials"},401
    
    token = create_access_token(identity=str(user.id))

    return {"token": token}

@app.route('/profile',methods=['GET'])
@jwt_required()
def profile():
    user_id = int(get_jwt_identity())
    return {"message": f"welcome user {user_id}"}

@app.route('/log',methods=['POST'])
@jwt_required()
def log_api():
    data=request.json

    endpoint=data.get('endpoint')
    response_time=data.get('response_time')
    status=data.get('status')

    user_id=get_jwt_identity()

    new_log=APILog(
        endpoint=endpoint,
        response_time=response_time,
        status=status,
        user_id=int(user_id)
    )
    db.session.add(new_log)
    db.session.commit()

    return {"message": "Log stored successfully"}


@app.route('/')
def home():
    return{"message":"Devtrack Running"}

if __name__=="__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)