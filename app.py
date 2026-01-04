from flask import Flask, render_template, request, redirect, session
import os
from openai import OpenAI

# ---------------- BASIC CONFIG ----------------
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dwarka-secret-key")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

USERS_FILE = "users.txt"
CHAT_DIR = "chats"

if not os.path.exists(CHAT_DIR):
    os.mkdir(CHAT_DIR)

# ---------------- USER HELPERS ----------------
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

# ---------------- CHAT HELPERS ----------------
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

# ---------------- ROUTES ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        users = load_users()
        if username in users and users[username] == password:
            session["username"] = username
            return redirect("/chat")

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

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
        msg = request.form.get("message", "").strip()

        if msg:
            save_message(username, "user", msg)

            system_prompt = system_prompt = """
You are Panda 🐼, an AI Study Buddy for Indian students.

STRICT RULES (MUST FOLLOW):
- NEVER start replies with filler like:
  "Sure", "Absolutely", "Here’s", "Let’s", "I can help"
- NEVER say what you are going to explain
- ALWAYS start directly with the answer
- If steps are required, START WITH STEP 1 immediately
- Give full, complete answers in ONE response
- Do NOT wait for follow-up like "do then" or "where are steps"
- Explain like a calm, experienced teacher
- Use simple English suitable for exams
- If answer is long, structure using numbered points

Tone:
Friendly, confident, motivating

Identity:
You are Panda 🐼 – Dwarka Study Buddy.
"""

            messages = [{"role": "system", "content": system_prompt}]

            # Add last 10 messages only (safe memory)
            for m in chat_history[-10:]:
                messages.append(m)

            messages.append({"role": "user", "content": msg})

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=500
                )

                reply = response.choices[0].message.content.strip()

                if len(reply) > 30:
                    save_message(username, "assistant", reply)

            except Exception:
                save_message(
                    username,
                    "assistant",
                    "🐼 Panda is a little tired right now. Please try again in a moment."
                )

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


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

