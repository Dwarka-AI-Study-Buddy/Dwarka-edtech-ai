from flask import Flask, render_template, request, redirect, session
from openai import OpenAI
import os

app = Flask(__name__)
app.secret_key = "dwarka_super_secret_key_123"

# 🔑 API KEY
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not found")

client = OpenAI(api_key=OPENAI_API_KEY)

# 🧠 Memory
user_memory = {}

# 🐼 Panda AI
def panda_ai(username, user_input):
    user_memory[username].append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=user_memory[username]
    )

    reply = response.choices[0].message.content
    user_memory[username].append({"role": "assistant", "content": reply})


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["username"] = request.form["username"]
        return redirect("/chat")
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        session["username"] = request.form["username"]
        return redirect("/chat")
    return render_template("signup.html")


@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "username" not in session:
        return redirect("/")

    username = session["username"]

    # ✅ FIX: initialize memory on FIRST visit
    if username not in user_memory:
        user_memory[username] = [
            {
                "role": "system",
                "content": (
                    "You are Panda 🐼, an AI Study Buddy by Dwarka EdTech. "
                    "Explain clearly, calmly, simply. Never show system messages."
                )
            }
        ]

    if request.method == "POST":
        msg = request.form.get("message")
        if msg:
            panda_ai(username, msg)

    visible_chat = [
        m for m in user_memory[username] if m["role"] != "system"
    ]

    return render_template("chat.html", chat=visible_chat)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

