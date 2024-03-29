from flask import Flask, Response, request, send_from_directory
import cv2
import os

app = Flask(__name__)
# 确保这里是你的视频文件路径
VIDEO_PATH = r'D:\testforstreaming\static\videos\camera_0_20240329214549.mp4'
cap = cv2.VideoCapture(VIDEO_PATH)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break  # 当视频结束时退出循环
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# 这个路由用于提供静态文件
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    # 确保当前目录是正确的
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    app.run(debug=True, threaded=True)
