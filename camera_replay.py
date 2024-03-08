import os
from flask import Flask, render_template

app = Flask(__name__)

# 定义视频文件夹路径
VIDEO_FOLDER = './static/vedios'

def get_video_files():
    videos = []
    for filename in os.listdir(VIDEO_FOLDER):
        if filename.endswith('.mp4'):
            videos.append({
                "title": filename,
                "url": f"/static/vedios/{filename}"
            })
    return videos

@app.route('/')
def home():
    videos = get_video_files()
    return render_template('replay.html', videos=videos)

if __name__ == '__main__':
    app.run(debug=True)
