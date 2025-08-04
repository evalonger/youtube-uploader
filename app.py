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
import json

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

scheduler.start()

scheduled_videos = []
scheduler = BackgroundScheduler()



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
        publish_time = request.form['publish_time']  # HH:MM

        video_path = os.path.join(UPLOAD_FOLDER, video.filename)
        video.save(video_path)

        publish_datetime = publish_date + ' ' + publish_time

        # Planı scheduled.json'a yaz
        with open("scheduled.json", "r+") as file:
            data = json.load(file)
            data.append({
                "video_path": video_path,
                "title": title,
                "description": description,
                "tags": tags,
                "publish_datetime": publish_datetime
            })
            file.seek(0)
            json.dump(data, file, indent=2)
        
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
    print(f"[DEBUG] Video yüklendi! Video ID: {response['id']}")

    return f"https://youtu.be/{response['id']}"
    
    
def kontrol_et_ve_yukle():
    print(f"[{datetime.now()}] Scheduler çalışıyor, planlanan videolar kontrol ediliyor...")
    try:
        with open("scheduled.json", "r+") as file:
            data = json.load(file)
            kalan_videolar = []
            for item in data:
                zaman = datetime.strptime(item["publish_datetime"], "%Y-%m-%d %H:%M")
                if datetime.now() >= zaman:
                    try:
                        upload_to_youtube(
                            item["video_path"],
                            item["title"],
                            item["description"],
                            item["tags"]
                        )
                        print(f"Yüklendi: {item['title']}")
                    except Exception as e:
                        print(f"Yükleme hatası: {str(e)}")
                        kalan_videolar.append(item)  # Tekrar denemek için sakla
                else:
                    kalan_videolar.append(item)
            file.seek(0)
            file.truncate()
            json.dump(kalan_videolar, file, indent=2)
    except Exception as e:
        print(f"Kontrol hatası: {str(e)}")
        
scheduler.add_job(kontrol_et_ve_yukle, 'interval', minutes=1)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
