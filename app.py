from flask import Flask, render_template, request, redirect, session
import os
from openai import OpenAI

# ------------------ APP SETUP ------------------
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dwarka-secret-key")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

USERS_FILE = "users.txt"
CHAT_DIR = "chats"

if not os.path.exists(CHAT_DIR):
    os.makedirs(CHAT_DIR)

# ------------------ USER HELPERS ------------------
def load_users():
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if "|" in line:
                    u, p = line.strip().split("|", 1)
                    users[u] = p
    return users

def save_user(username, password):
    with open(USERS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{username}|{password}\n")

# ------------------ CHAT HELPERS ------------------
def chat_file(username):
    return os.path.join(CHAT_DIR, f"{username}.txt")

def load_chat(username):
    messages = []
    file = chat_file(username)
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                if "|" in line:
                    role, content = line.strip().split("|", 1)
                    messages.append({"role": role, "content": content})
    return messages

def save_message(username, role, content):
    with open(chat_file(username), "a", encoding="utf-8") as f:
        f.write(f"{role}|{content}\n")

# ------------------ ROUTES ------------------
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
    chat_history = load_chat(username)

    if request.method == "POST":
        user_msg = request.form.get("message")

        if user_msg:
            save_message(username, "user", user_msg)

            system_prompt = """
You are Panda 🐼, an AI Study Buddy and Teacher.

MANDATORY RULES:
- Always give FULL answers, never stop at point 1
- Explain step-by-step
- Minimum 6–8 points for broad topics
- Each point must have explanation
- Simple English, beginner friendly
- Exam + real-life focused
- Do NOT ask follow-up questions
- Do NOT give short answers
- Start directly with explanation

Identity:
You are Panda 🐼 – Dwarka Study Buddy.
"""

            messages = [
                {"role": "system", "content": system_prompt},
                *chat_history[-10:],  # last 10 messages only
                {"role": "user", "content": user_msg}
            ]

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=700,
                    temperature=0.6
                )

                reply = response.choices[0].message.content.strip()
                save_message(username, "assistant", reply)

            except Exception as e:
                save_message(username, "assistant", "⚠️ Error generating response. Please try again.")

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


# ------------------ RUN ------------------
if __name__ == "__main__":
    app.run(debug=True)
