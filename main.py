from flask import Flask, jsonify, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO, send
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from email_sender import send_verification_email
from flask import render_template
from extensions import db, User
from flask_migrate import Migrate
from functools import wraps

app = Flask(__name__)
socketio = SocketIO(app)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = "aVery$tr0ngSecretKey!12345&"
db.init_app(app)
with app.app_context():
    db.create_all()
migrate = Migrate(app, db)



@app.route("/")
def home():
    return render_template("index.html")


#   R E G I S T R A T I O N
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    hashed_password = generate_password_hash(data['password'])
    
    new_user = User(email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    send_verification_email(data['email'])

    return jsonify({'message': 'Registretion succesfull! Check your email'})


#   V E R I F Y C A T I O N
@app.route('/verify/<token>', methods=['GET'])
def verify_email(token):
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        user = User.query.filter_by(email=data['email']).first()

        if user:
            user.is_verified = True
            db.session.commit()
            return jsonify({"message": "Email confirmed!"})
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token is not active. Try again"}), 400
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token!"}), 400


#   L O G I N
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()

    if user and check_password_hash(user.password, data['password']):
        if not user.is_verified:
            return jsonify({"message": "Confirm your e-mail before login!"}), 403
        session['user_id'] = user.id
        token = jwt.encode({"user_id": user.id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
                           app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({"token": token})

    return jsonify({"message": "Incorrect email or password!"}), 401


#   T O K E N   C H E C K
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return render_template("index.html")

        try:
            token = token.split("Bearer ")[-1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data["user_id"])

            if not current_user:
                render_template("index.html")
            
        except jwt.ExpiredSignatureError:
            return render_template("index.html")
        except jwt.InvalidTokenError:
            render_template("index.html")
        return f(current_user, *args, **kwargs)

    return decorated


#   L O G I N   C H E C K
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return render_template('index.html')
        return f(*args, **kwargs)
    return decorated_function


#   H O M E     P A G E
@app.route('/home', methods=['GET'])
@login_required
def home_page():
    user_id = session['user_id']
    user = User.query.get(user_id)
    return render_template("home.html", user=user)


#   L O G O U T
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))


#   M E S S A G E
@socketio.on('send_message')
def handle_message(msg):
    user_id = session.get("user_id")
    if user_id:
        user = User.query.get(user_id)
    if msg.strip():
        formated_message = f'<a href="mailto:{user.email}">{user.email}</a>: {msg}'
        print(f"MSG -> {formated_message}")
        send(formated_message, broadcast=True)


#   P R O F I L E
@socketio.on('/profile')
def profile():
    user_id = session['user_id']
    user = User.query.get(user_id)
    email_show = f'<a style="font:bold;">E-Mail</a>: <a style="color:blue;">{user.email}</a>'
    send(email_show, broadcast=True)
    return render_template('profile.html', user=user)


if __name__ == "__main__":
    socketio.run(app)
    app.run(debug=True)
