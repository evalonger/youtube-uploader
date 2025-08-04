from flask import Flask, render_template, request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

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

        try:
            youtube_link = upload_to_youtube(video_path, title, description, tags)
            return f" Video yüklendi! <a href='{youtube_link}' target='_blank'>{youtube_link}</a>"
        except Exception as e:
            return f" Hata oluştu: {str(e)}"

    return render_template('upload.html')
    
def authenticate_youtube():
    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
    creds = flow.run_local_server()
    return build("youtube", "v3", credentials=creds)

def upload_to_youtube(video_path, title, description, tags):
    youtube = authenticate_youtube()

    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    } 
    media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True)
    response = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    ).execute()

    return f"https://youtu.be/{response['id']}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
