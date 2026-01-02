from flask import Flask, render_template, request, redirect, session, url_for
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dwarka-secret-key")

USERS_FILE = "users.txt"
user_memory = {}

# ------------------ HELPERS ------------------

def load_users():
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            for line in f:
                u, p = line.strip().split("|")
                users[u] = p
    return users

def save_user(username, password):
    with open(USERS_FILE, "a") as f:
        f.write(f"{username}|{password}\n")

def init_memory(username):
    if username not in user_memory:
        user_memory[username] = []

# ------------------ ROUTES ------------------

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()
        if username in users and users[username] == password:
            session["username"] = username
            return redirect("/chat")

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()
        if username in users:
            return render_template("signup.html", error="User already exists")

        save_user(username, password)
        return redirect("/")

    return render_template("signup.html")


@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "username" not in session:
        return redirect("/")

    username = session["username"]
    init_memory(username)

    if request.method == "POST":
        msg = request.form.get("message")
        if msg:
            user_memory[username].append({"role": "user", "content": msg})
            user_memory[username].append({
                "role": "assistant",
                "content": "🤖 Panda AI is coming soon!"
            })

    return render_template("chat.html", chat=user_memory[username])


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
