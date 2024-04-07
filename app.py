from flask import Flask, jsonify, render_template, Response, send_from_directory
import cv2
from datetime import datetime
import subprocess
import os
import tkinter as tk
from tkinter import messagebox
import requests
import threading

FRAME_RATE = 20.0
RESOLUTION = (640, 480)

app = Flask(__name__)
camera_records = {}

def generate_frames(camera_id):
    if camera_id not in camera_records:
        camera_records[camera_id] = {'is_recording': False, 'camera': cv2.VideoCapture(camera_id)}
    camera = camera_records[camera_id]['camera']

    while True:
        success, frame = camera.read()
        if not success:
            break
        
        if camera_records[camera_id]['is_recording']:
            process = camera_records[camera_id]['video_writer']
            try:
                process.stdin.write(frame.tobytes())
            except BrokenPipeError:
                # FFmpeg进程已关闭
                pass
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# 建立writer
def start_video_writer(camera_id):
    output_dir_base = os.path.join(app.root_path, 'static', 'videos')
    output_dir = os.path.join(output_dir_base, f"camera_{camera_id}")  # 每个相机的专用文件夹
    os.makedirs(output_dir, exist_ok=True)  # 如果目录不存在，则创建它
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4"
    filepath = os.path.join(output_dir, filename)
    command = [
        'ffmpeg',
        '-y',  # 覆盖输出文件（如果存在）
        '-f', 'rawvideo',  # 输入格式
        '-vcodec','rawvideo',  # 输入编解码器
        '-pix_fmt', 'bgr24',  # OpenCV的默认像素格式
        '-s', '{}x{}'.format(*RESOLUTION),  # 分辨率
        '-r', str(FRAME_RATE),  # 帧率
        '-i', '-',  # 从stdin读取输入
        '-c:v', 'libx264',  # 输出视频编解码器
        '-pix_fmt', 'yuv420p',  # 输出像素格式
        '-preset', 'ultrafast',  # 编码速度与压缩率的平衡
        '-f', 'mp4',  # 输出格式
        filepath
    ]
    p = subprocess.Popen(command, stdin=subprocess.PIPE)
    return p, filepath

def detect_cameras(limit=1):
    available_cameras = []
    for i in range(limit):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                available_cameras.append(i)
            cap.release()
    return available_cameras

# 為特定相機初始化writer
@app.route('/start_recording/<camera_id>', methods=['GET'])
def start_recording(camera_id):
    camera_id = int(camera_id)
    if camera_id in camera_records and not camera_records[camera_id].get('is_recording', False):
        video_writer, filename = start_video_writer(camera_id)
        camera_records[camera_id].update({
            'is_recording': True,
            'filename': filename,
            'video_writer': video_writer,
        })
        return jsonify(success=True, filename=filename)
    elif camera_id not in camera_records:
        return jsonify(success=False, message="Camera not initialized for streaming")
    else:
        return jsonify(success=False, message="Recording already started")


@app.route('/stop_recording/<camera_id>', methods=['GET'])
def stop_recording(camera_id):
    camera_id = int(camera_id)
    if camera_id in camera_records and camera_records[camera_id]['is_recording']:
        camera_records[camera_id]['is_recording'] = False
        # 关闭FFmpeg进程的stdin
        camera_records[camera_id]['video_writer'].stdin.close()
        # 等待FFmpeg进程结束
        camera_records[camera_id]['video_writer'].wait()
        # 释放相机资源，如果需要
        # camera_records[camera_id]['camera'].release()
        return jsonify(success=True)
    return jsonify(success=False, message="Recording not started or already stopped")

@app.route('/list_videos/<int:camera_id>')
def list_videos(camera_id):
    output_dir_base = os.path.join(app.root_path, 'static', 'videos')
    output_dir = os.path.join(output_dir_base, f"camera_{camera_id}")  # 根据相机ID定位文件夹
    if not os.path.exists(output_dir):
        return jsonify(success=False, message="Video directory does not exist")

    videos = [file for file in os.listdir(output_dir)]
    return jsonify(success=True, videos=videos)

@app.route('/video/<int:camera_id>')
def video(camera_id):
    return Response(generate_frames(camera_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/trigger_notification')
def trigger_notification():
    # 标记通知已触发，等待前端轮询检查
    global notification_triggered
    notification_triggered = True
    return jsonify(success=True, message="Notification will be triggered")

# 前端轮询此路由以检查是否触发通知
@app.route('/check_notification')
def check_notification():
    global notification_triggered
    if notification_triggered:
        notification_triggered = False  # 确保重置状态
        return jsonify(trigger=True)
    else:
        return jsonify(trigger=False)

@app.route('/')
def index():
    camera_ids = detect_cameras()
    return render_template('page.html', camera_ids=camera_ids)

def run_gui():
    def trigger_flask_notification():
        try:
            # 通过发送请求到 Flask 应用的 /trigger_notification 路由来触发通知
            response = requests.get('http://127.0.0.1:5000/trigger_notification')
            if response.status_code == 200:
                print("Notification trigger sent to Flask.")
            else:
                print(f"Failed to send trigger. Status Code: {response.status_code}")
        except Exception as e:
            print(f"Error connecting to Flask server: {e}")

    # GUI 创建部分
    root = tk.Tk()
    root.title("Trigger Notification")
    trigger_button = tk.Button(root, text="触发通知", command=trigger_flask_notification)
    trigger_button.pack(pady=20)
    root.mainloop()

if __name__ == '__main__':
    # Flask 应用运行在主线程
    threading.Thread(target=run_gui, daemon=True).start()  # GUI 运行在一个独立的线程中
    app.run(debug=True, threaded=True, use_reloader=False)
