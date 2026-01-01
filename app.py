from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)

# ------------------- CONFIG -------------------
app.secret_key = os.getenv("SECRET_KEY", "dwarka-ai-secret-123")

AI_NAME = "Panda 🐼"

# ------------------- STORAGE -------------------
users = {}          # username -> password
user_memory = {}    # username -> chat history list


# ------------------- ROUTES -------------------

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username] == password:
            session["username"] = username
            user_memory.setdefault(username, [])
            return redirect(url_for("chat"))
        else:
            return "Invalid credentials"

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users:
            return "User already exists"

        users[username] = password
        user_memory[username] = []
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]

    if request.method == "POST":
        user_msg = request.form["message"].strip()

        if user_msg:
            # Save USER message
            user_memory[username].append({
                "role": "user",
                "content": user_msg
            })

            # SIMPLE AI REPLY (replace later with OpenAI)
            ai_reply = f"I am {AI_NAME}, your AI Study Buddy. You asked: {user_msg}"

            # Save AI reply
            user_memory[username].append({
                "role": "ai",
                "content": ai_reply
            })

    # ONLY send user + ai messages to UI
    visible_chat = [
        msg for msg in user_memory.get(username, [])
        if msg["role"] in ["user", "ai"]
    ]

    return render_template(
        "chat.html",
        chat=visible_chat,
        ai_name=AI_NAME
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ------------------- MAIN -------------------
if __name__ == "__main__":
    app.run(debug=True)
