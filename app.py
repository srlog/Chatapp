from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase
from ai import ask

app = Flask(__name__)

app.config["SECRET_KEY"] = "Thisisanflaskapplicationbuildforstudentstochatandcleartheirdoubts"



socketio = SocketIO(app)

rooms = {}

users = {'user':'1234','student':'password','teacher':'password'}

@app.route('/register',methods=["POST","GET"])
def register():
    if request.method== "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password == confirm_password :
            users[username] = password
            return redirect(url_for("login"))
        else:
            return render_template("register.html",error = "Password and confirm password doesn't match.")

    return render_template("register.html")


@app.route('/')
@app.route('/login', methods=['POST','GET'])
def login():
    if session.get("loggedin") :
        return redirect("homepage")
    if request.method == "POST" :
        username = request.form.get("username")
        password = request.form.get('password')
        designation = request.form.get("designation", 'Student')
        if username not in users.keys():
            error = "Username doesn't exist."
            return render_template("login.html",error=error)


        if password == users.get(username):
            pass
            session['name']=username
            session['designation']=designation
            session["loggedin"]=True

            return redirect(url_for('homepage'))
        else:
            error = "Password is incorrect."
            return render_template("login.html",error=error)
    
    return render_template("login.html")

@app.route('/homepage')
def homepage():

    if session.get("loggedin"):
        name = session.get('name')
        designation = session.get('designation')
        room_name= []
        for key in rooms:
            room = rooms.get(key)
            print(room)
            room_name.append([room.get('topic'),key])

        return render_template('homepage.html',name=name,designation=designation,room_name=room_name)
    
    return redirect('login')

@app.route('/logout')
def logout():
    session['loggedin']=False
    return redirect(url_for('login'))


def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        
        if code not in rooms:
            break
    
    return code

@app.route("/chat", methods=["POST", "GET"])
def home():
    if not session.get("loggedin") :
        return redirect(url_for("homepage"))
    
    name = session.get("name")
    designation = session.get("designation")
    session["name"]= name
    session["designation"] = designation
    if request.method == "POST":
        name = session.get("name")
        designation = session.get("designation")
      
        topic = request.form.get("topic")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)


        if join != False and not code:
            return render_template("select.html", error="Please enter a room code.", code=code, topic=topic)
        
        room = code
        if create != False:
            room = generate_unique_code(6)
            rooms[room] = {"designation":designation,"topic":topic,"members": 0, "messages": []}
        elif code not in rooms:
            return render_template("select.html", error="Room does not exist.", code=code, topic=topic)
        
        if not topic:
            return render_template("select.html", error="Please enter a Topic.", code=code, topic=topic)
        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))

    return render_template("select.html")

@app.route("/room")
def room():
    if not session.get("loggedin"):
        return redirect(url_for('login'))
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:    
        return redirect(url_for("home"))

    return render_template("room.html", code=room, messages=rooms[room]["messages"], topic = rooms[room]["topic"], designation = session.get("designation"))

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return 
    print(rooms[room])
    content = {
        "name": session.get("name"),
        "designation" : session.get("designation","Student"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    if ('@ai' in data["data"].lower()) or ('@alas' in data["data"].lower()):
        resp = ask(data["data"])
        contentai = {
            "name": "Ana",
            "designation" : session.get("designation","Your slave"),
            "message": resp
        }
        send(contentai,to=room)
        rooms[room]["messages"].append(contentai)
        print(f"AI said: {resp} to {session.get('name')}")

    print(f"{session.get('name')} said: {data['data']}")
    

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    designation = session.get("designation")
    if not room or not name:

        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "designation":designation,"message": "joined the discussion"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined the discussion {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    designation = session.get("designation")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    
    send({"name": name, "designation":designation, "message": "has left the discussion"}, to=room)
    print(f"{name} has left the discussion {room}")

@app.route("/clearall")
def clear():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    socketio.run(app, debug=True)