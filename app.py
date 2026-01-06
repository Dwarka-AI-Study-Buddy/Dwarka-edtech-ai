from flask import Flask, render_template, request, redirect, session
import os
from openai import OpenAI

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dwarka-secret-key")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

USERS_FILE = "users.txt"
CHAT_DIR = "chats"

if not os.path.exists(CHAT_DIR):
    os.makedirs(CHAT_DIR)

# ---------------- USERS ----------------
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

# ---------------- CHAT ----------------
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

# ---------------- ROUTES ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users = load_users()
        u = request.form.get("username")
        p = request.form.get("password")

        if u in users and users[u] == p:
            session["username"] = u
            return redirect("/chat")

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        users = load_users()
        u = request.form.get("username")
        p = request.form.get("password")

        if u in users:
            return render_template("signup.html", error="User already exists")

        save_user(u, p)
        return redirect("/")

    return render_template("signup.html")


@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "username" not in session:
        return redirect("/")

    username = session["username"]
    history = load_chat(username)

    if request.method == "POST":
        user_msg = request.form.get("message")

        if user_msg:
            save_message(username, "user", user_msg)

            # 🔥 STRONG SYSTEM PROMPT (THIS FIXES EVERYTHING)
            system_prompt = """
You are Panda 🐼 – an expert teacher and study mentor.

ABSOLUTE RULES (NO EXCEPTIONS):
1. Always give COMPLETE explanations
2. Minimum 8–12 numbered points for topics like:
   - Product Management
   - Career
   - Exams
   - Technology
3. EACH point must have:
   - Clear heading
   - 3–4 line explanation
   - Example if possible
4. NEVER stop mid-answer
5. NEVER say "Here is a breakdown" and stop
6. NEVER ask follow-up questions
7. Assume student is a beginner
8. Explain like a real teacher in class

Tone:
• Friendly
• Confident
• Structured
• Exam + practical focused

Identity:
You are Panda 🐼 – Dwarka AI Study Buddy.
"""

            messages = [
                {"role": "system", "content": system_prompt},
                *history[-8:],   # keep memory short but effective
                {"role": "user", "content": user_msg}
            ]

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.4,
                    max_tokens=1000
                )

                reply = response.choices[0].message.content.strip()
                save_message(username, "assistant", reply)

            except Exception:
                save_message(username, "assistant", "⚠️ Panda is tired. Please try again.")

        return redirect("/chat")

    return render_template("chat.html", chat=load_chat(username))


@app.route("/clear")
def clear():
    if "username" in session:
        f = chat_file(session["username"])
        if os.path.exists(f):
            os.remove(f)
    return redirect("/chat")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
