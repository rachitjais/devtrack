from flask import Flask,request
from models import db,User
from flask_jwt_extended import JWTManager, create_access_token

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
    
    token = create_access_token(identity=user.id)

    return {"token": token}


@app.route('/')
def home():
    return{"message":"Devtrack Running"}

if __name__=="__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)