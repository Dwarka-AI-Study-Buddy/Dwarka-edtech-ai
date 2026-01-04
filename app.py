from flask import Flask, render_template, request, redirect, session
import os
from openai import OpenAI

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dwarka-secret-key")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

USERS_FILE = "users.txt"
CHAT_DIR = "chats"

if not os.path.exists(CHAT_DIR):
    os.mkdir(CHAT_DIR)

# ---------- USER HELPERS ----------
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

# ---------- CHAT HELPERS ----------
def chat_file(username):
    return os.path.join(CHAT_DIR, f"{username}.txt")

def load_chat(username):
    messages = []
    file = chat_file(username)
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                role, content = line.strip().split("|", 1)
                messages.append({"role": role, "content": content})
    return messages

def save_message(username, role, content):
    with open(chat_file(username), "a", encoding="utf-8") as f:
        f.write(f"{role}|{content}\n")

# ---------- ROUTES ----------
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
    chat_history = load_chat(username)

    if request.method == "POST":
        msg = request.form.get("message")
        if msg:
            save_message(username, "user", msg)

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are Panda 🐼, a friendly AI Study Buddy."},
                    *chat_history,
                    {"role": "user", "content": msg}
                ],
                max_tokens=300
            )

            reply = response.choices[0].message.content
            save_message(username, "assistant", reply)

        return redirect("/chat")

    chat_history = load_chat(username)
    return render_template("chat.html", chat=chat_history)


@app.route("/clear")
def clear_chat():
    if "username" in session:
        file = chat_file(session["username"])
        if os.path.exists(file):
            os.remove(file)
    return redirect("/chat")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
