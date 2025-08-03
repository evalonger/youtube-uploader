from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
if __name__ == "_main_":
    app.run(host="0.0.0.0", port=5000)
