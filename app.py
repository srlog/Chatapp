from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO


app = Flask(__name__)

socketio = SocketIO(app)


@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST','GET'])
def login():
    username = request.form['username']
    regno = request.form['regno']
    email = request.form['email']

    if not username or not regno or not email:
        return "All fields are required", 400

    if not regno.isdigit() or len(regno) != 6:
        return "Register number must be a 6 digit number", 400

    if '@' not in email or '.' not in email.split('@')[-1]:
        return "Invalid email format", 400

    return redirect(url_for('homepage'))

@app.route('/homepage')
def homepage():
    return render_template('homepage.html')

@app.route('/chat')
def chat():
    
    return render_template("room.html")

def logout():
    return redirect(url_for('home'))

def changeUser():
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
