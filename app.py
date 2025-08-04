from flask import Flask, render_template, request
app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        video = request.files['video']
        title = request.form['title']
        description = request.form['description']
        tags = request.form['tags'].split(',')

        video_path = os.path.join(UPLOAD_FOLDER, video.filename)
        video.save(video_path)

        # Şimdilik kontrol amaçlı
        return f"Başlık: {title}<br>Açıklama: {description}<br>Etiketler: {tags}<br>Dosya: {video_path}"

    return render_template('upload.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
