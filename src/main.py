from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def render():
    return render_template("index.html")

@app.route('/admin')
def admin():
    return render_template('admin.html')

print("bruh")