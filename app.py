from flask import Flask, jsonify, render_template, Response, send_from_directory
import cv2
from datetime import datetime

FRAME_RATE = 20.0
RESOLUTION = (640, 480)

app = Flask(__name__)
camera_records = {}

def generate_frames(camera_id):
    camera = cv2.VideoCapture(camera_id)
    while True:
        # for Recording
        if camera_id in camera_records and camera_records[camera_id]['is_recording']:
            video_writer = camera_records[camera_id]['video_writer']
            video_writer.write(frame)

        # for Streaming
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    # 直接返回已經修改好的HTML內容
    return render_template('page.html')

@app.route('/video/<camera_id>')
def video(camera_id):
    return Response(generate_frames(int(camera_id)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def start_video_writer(camera_id, frame):
    filename = f"camera_{camera_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.avi"
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(filename, fourcc, FRAME_RATE, RESOLUTION)
    return out, filename

# 启动录制
@app.route('/start_recording/<camera_id>', methods=['POST'])
def start_recording(camera_id):
    camera_id = int(camera_id)
    if camera_id not in camera_records:
        # 获取第一帧来确定分辨率
        camera = cv2.VideoCapture(camera_id)
        success, frame = camera.read()
        if success:
            video_writer, filename = start_video_writer(camera_id, frame)
            camera_records[camera_id] = {
                'is_recording': True,
                'filename': filename,
                'video_writer': video_writer,
                'camera': camera,  # 保持摄像头对象开启
            }
            return jsonify(success=True, filename=filename)
        else:
            return jsonify(success=False, message="Could not read from camera")
    return jsonify(success=False, message="Recording already started")

# 停止录制
@app.route('/stop_recording/<camera_id>', methods=['POST'])
def stop_recording(camera_id):
    camera_id = int(camera_id)
    if camera_id in camera_records and camera_records[camera_id]['is_recording']:
        # 停止录制并释放资源
        camera_records[camera_id]['is_recording'] = False
        camera_records[camera_id]['video_writer'].release()
        camera_records[camera_id]['camera'].release()  # 关闭摄像头对象
        return jsonify(success=True)
    return jsonify(success=False, message="Recording not started or already stopped")

if __name__ == '__main__':
    app.run(debug=True)
