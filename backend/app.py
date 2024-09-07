from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db  # Import the db object from models.py
import psycopg2
import os
from flask_restx import Api, Resource, fields
import hashlib  # Instead of import sha256

app = Flask(__name__)
api = Api(app)

# Define the namespace
ns = api.namespace('api', description='API operations')

# Define the user model
user_model = api.model('User', {
    'email': fields.String(required=True, description='User email')
})

message_model = api.model('Message', {
    'message': fields.String(required=True, description='Chat message')
})

@ns.route('/register')
class UserRegister(Resource):
    @ns.expect(user_model)
    @ns.response(201, 'User registered successfully')
    @ns.response(400, 'User already registered')
    def post(self):
        data = api.payload
        email = data['email']
        email_hash = hash_email(email)
        
        try:
            conn = psycopg2.connect("dbname=test user=postgres")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (email_hash) VALUES (%s)", (email_hash,))
            conn.commit()
            cursor.close()
            conn.close()
            return {'message': 'User registered successfully!'}, 201
        except Exception as e:
            return {'message': 'User already registered!'}, 400

@ns.route('/chat/<int:group_id>')
class Chat(Resource):
    @ns.response(200, 'Success')
    def get(self, group_id):
        conn = psycopg2.connect("dbname=socolab_hamburg user=liushangqing")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM chat WHERE group_id = %s ORDER BY sent_at", (group_id,))
        messages = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(messages)

    @ns.expect(message_model)
    @ns.response(200, 'Message sent successfully')
    def post(self, group_id):
        conn = psycopg2.connect("dbname=socolab_hamburg user=liushangqing")
        data = request.json
        message = data['message']
        user_id = 1  # This should come from the logged-in user session
        cursor = conn.cursor()
        cursor.execute("INSERT INTO chat (group_id, user_id, message) VALUES (%s, %s, %s)", 
                       (group_id, user_id, message))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Message sent!'})

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://liushangqing:test@localhost/socolab_hamburg'

# Initialize the database and migrations
db.init_app(app)
migrate = Migrate(app, db)

def hash_email(email):
    return hashlib.sha256(email.encode()).hexdigest()


if __name__ == '__main__':
    app.run(debug=True)
