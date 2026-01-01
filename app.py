from flask import Flask, render_template, request, redirect, session
import openai
import os

app = Flask(__name__)
app.secret_key = "dwarka-ai-secret-123"

OPENAI_KEY = os.getenv("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")

if not OPENAI_KEY:
    print("⚠️ OPENAI_API_KEY not found")
else:
    openai.api_key = OPENAI_KEY


# 🧠 Memory per user
user_memory = {}

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            with open("users.txt", "r") as f:
                for line in f:
                    u, p = line.strip().split(",", 1)
                    if u == username and p == password:
                        session["username"] = username
                        return redirect("/chat")
        except FileNotFoundError:
            pass

        return "Invalid login"

    return render_template("login.html")


# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with open("users.txt", "a") as f:
            f.write(username + "," + password + "\n")

        return redirect("/")

    return render_template("signup.html")


# ---------------- PANDA AI ----------------
def panda_ai(username, user_input):
    if username not in user_memory:
        user_memory[username] = [
            {
                "role": "system",
                "content": "I am Panda, your AI Study Buddy"
                    "Help You In Your Style.."
            }
        ]

    user_memory[username].append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=user_memory[username]
    )

    reply = response.choices[0].message.content
    user_memory[username].append({"role": "assistant", "content": reply})

    return reply


# ---------------- CHAT ----------------
@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "username" not in session:
        return redirect("/")

    username = session["username"]

    if request.method == "POST":
        msg = request.form["message"]
        panda_ai(username, msg)

    return render_template("chat.html", chat=user_memory.get(username, []))


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)






