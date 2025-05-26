from flask import Flask, redirect, url_for, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/home")
def home():
    return "Hello this is the home page"


@app.route("/about")
def about():
    return render_template("about.html")



@app.route("/log-in")
def login():
    return render_template("login.html")


@app.route("/sign-up")
def signup():
    return render_template("signup.html")


@app.route("/contactus")
def contactus():
    return render_template("contactus.html")


@app.route("/admin")
def admin():
    return redirect(url_for('index'))  # You can redirect to any valid endpoint


if __name__ == "__main__":
    app.run(debug=True)
