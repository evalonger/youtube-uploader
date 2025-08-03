from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Buraya video yükleme işlemi kodunu ekleyeceğiz ileride
        return "Video yükleme işlemi burada yapılacak."
    else:
        return render_template('upload.html')
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
