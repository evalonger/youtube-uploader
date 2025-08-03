from flask import Flask, render_template, request
app = Flask(__name__)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def authenticate_youtube():
    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
    creds = flow.run_local_server(port=0)
    return build("youtube", "v3", credentials=creds)

def upload_video(video_file, title, description, tags):
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
    media = MediaFileUpload(video_file, mimetype="video/mp4", resumable=True)
    response = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    ).execute()
    return f"https://youtu.be/{response['id']}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    video_url = upload_video(
        video_file="55.mp4",
        title="Test Shorts Başlığı",
        description="Açıklama burada",
        tags=["shorts", "test"]
    )
    return f"Video yüklendi: <a href='{video_url}'>{video_url}</a>"
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
