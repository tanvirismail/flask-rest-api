from dataclasses import field
from email.policy import strict
from flask import Flask, redirect, render_template, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from datetime import datetime
import uuid
from  werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, EmailField, validators
from werkzeug.datastructures import ImmutableMultiDict

# Init app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'

# Database
dbname = 'postgres'
host = 'localhost'
username = 'postgres'
password = 'postgres'
port = '5432'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://"+username+":"+password+"@"+host+":"+port+"/"+dbname
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# Init DB
db = SQLAlchemy(app)
#Init marshmallow
ma = Marshmallow(app)
#init migrate
migrate = Migrate(app, db)

# model
class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # def __init__(self, content, completed, created_at):
    #     self.content = content
    #     self.completed = completed
    #     self.created_at = created_at
    
    # def __repr__(self) -> str:
    #     # return super().__repr__()
    #     return '<Task %r>' % self.id

# schema
class TodoSchema(ma.Schema): # ma.ModelSchema
    class Meta:
        fields = ('id','content','completed','created_at')
        
# class TodoSchema(ma.ModelSchema):
#     class Meta:
#         model = Todo
    
# init schema
todo_schema = TodoSchema()
todos_schema = TodoSchema(many=True)
        
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id','name','email','password','created_at')
        
user_schema = UserSchema()
users_schema = UserSchema(many=True)


@app.route("/users", methods=['GET'])
def get_users():
    if request.method == 'GET':
        users = User.query.order_by(User.created_at.desc()).all()
        return users_schema.jsonify(users)
    
class userFromRequest(FlaskForm):
    class Meta:
        csrf = False
    name =  StringField('name', validators=[ 
        validators.InputRequired('The name is required.'),
        validators.Length(min=- 1, max= 60, message='mininum 1 to maximum 60 charecter is required.')
    ])
    email = EmailField('email', validators=[ 
        validators.InputRequired('The email is required.'),
        validators.Length(min=- 1, max= 150, message='mininum 1 to maximum 150 charecter is required.'),
        validators.Email(message='Invalid Email.')
    ])
    password = PasswordField('password',validators=[
        validators.InputRequired('The password is required.'),
        validators.Length(min= 4, max= 32, message='mininum 4 to maximum 32 charecter is required.'),
        validators.EqualTo('confirm_password', message='password not match.')
    ])
    confirm_password = PasswordField('Repeat Password')
    
    def validate_email(form, field):
        user = User.query.filter_by( email=field.data ).first()
        if user:
            raise validators.ValidationError('This email was exists.')
    

@app.route("/register", methods=['POST'])
def register():
    if request.method == 'POST':
        # validation
        form = userFromRequest()
        if form.validate():
            name = request.json['name']
            email = request.json['email']
            password = generate_password_hash(request.json['password'], method='sha256')
            register = User(name=name, email=email, password=password)
            try:
                db.session.add(register)
                db.session.commit()
                return user_schema.jsonify(register)
            except:
                return jsonify({'message':'Something wrong.'})
        else:
            return jsonify({'message':'The given data was invalid.','errors':form.errors})
        
@app.route("/load-user/<id>", methods=['GET'])
def load_user(id):
    if request.method == 'GET':
        user =  User.query.filter_by( id=id ).first()
        return user_schema.jsonify(user)    
  
  
  
  
  
  
  


# route
@app.route("/", methods=['GET'])
def index():
    if request.method == 'GET':
        tasks = Todo.query.order_by(Todo.created_at.desc()).all()
        return todos_schema.jsonify(tasks)
    
@app.route("/add-task", methods=['POST'])
def add_task():
    if request.method == 'POST':
        task_content = request.json['content']
        if task_content == '':
            return jsonify({'message':'Invalid input'}), 422
        else:
            new_task = Todo(content=task_content)
            try:
                db.session.add(new_task)
                db.session.commit()
                return todo_schema.jsonify(new_task)
            except:
                return jsonify({'message':'Invalid input'})

@app.route("/delete/<int:id>")
def delete(id):
    task = Todo.query.get_or_404(id)
    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message':'Successfuly deleted'})
    except:
        return jsonify({'message':'something wrong!'}), 422

@app.route("/show/<int:id>", methods=['GET'])
def show(id):
    task = Todo.query.get_or_404(id)
    return todo_schema.jsonify(task)

@app.route("/edit/<int:id>", methods=['POST'])
def edit(id):
    if request.method == 'POST':
        task = Todo.query.get_or_404(id)
        if request.json['content'] == '' and task :
            return jsonify({'message':'Invalid input'}), 422
        else:
            try:
                task.content = request.json['content']
                task.completed =  request.json.get('completed')
                db.session.commit()
                return todo_schema.jsonify(task)
            except:
                return jsonify({'message':'Something wrong'}), 422



# Run server
if __name__ == "__main__":
    app.run(debug=True)

