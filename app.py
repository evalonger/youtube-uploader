from flask import Flask, render_template, request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import pickle
from googleapiclient.discovery import build
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import threading

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

scheduled_videos = []
scheduler = BackgroundScheduler()
scheduler.start()

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
        publish_date = request.form['publish_date']  # yyyy-mm-dd
        publish_time = request.form['publish_time']  # HH:MM formatında

        video_path = os.path.join(UPLOAD_FOLDER, video.filename)
        video.save(video_path)

        publish_datetime = datetime.strptime(publish_date + ' ' + publish_time, '%Y-%m-%d %H:%M')
        
        scheduled_videos.append({
            'video_path': video_path,
            'title': title,
            'description': description,
            'tags': tags,
            'publish_datetime': publish_datetime
        })

        # Scheduler’a iş ekle
        scheduler.add_job(
            func=upload_to_youtube,
            trigger='date',
            run_date=publish_datetime,
            args=[video_path, title, description, tags]
        )
        return f"Video planlandı! Yayınlanacak: {publish_datetime}"
        

    return render_template('upload.html')
    
def authenticate_youtube():
    with open("token.pickle", "rb") as token_file:
        creds = pickle.load(token_file)
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
