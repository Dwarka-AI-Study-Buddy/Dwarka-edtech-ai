from flask import Flask, render_template, request, redirect, session
import os
from openai import OpenAI

# ---------------- APP SETUP ----------------
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dwarka-secret-key")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

USERS_FILE = "users.txt"
user_memory = {}

# ---------------- HELPERS ----------------
def load_users():
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            for line in f:
                if "|" in line:
                    u, p = line.strip().split("|", 1)
                    users[u] = p
    return users

def save_user(username, password):
    with open(USERS_FILE, "a") as f:
        f.write(f"{username}|{password}\n")

def init_memory(username):
    if username not in user_memory:
        user_memory[username] = [
            {
                "role": "system",
                "content": (
                    "You are Panda 🐼, an AI Study Buddy from Dwarka. "
                    "Explain topics simply, clearly, with examples. "
                    "Be friendly, motivating, and student-focused."
                )
            }
        ]

def panda_ai(username, user_msg):
    user_memory[username].append({"role": "user", "content": user_msg})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=user_memory[username],
        max_tokens=300
    )

    ai_reply = response.choices[0].message.content
    user_memory[username].append({"role": "assistant", "content": ai_reply})

# ---------------- ROUTES ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        users = load_users()
        if username in users and users[username] == password:
            session["username"] = username
            return redirect("/chat")

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

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
            panda_ai(username, msg)

    visible_chat = [
        m for m in user_memory[username]
        if m["role"] != "system"
    ]

    return render_template("chat.html", chat=visible_chat)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)


