from flask import Flask, jsonify, render_template, Response
import cv2
from datetime import datetime

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
            video_writer = camera_records[camera_id]['video_writer']
            video_writer.write(frame)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# 建立writer
def start_video_writer(camera_id):
    filename = f"camera_{camera_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4"
    # 尝试使用H.264编码
    fourcc = cv2.VideoWriter_fourcc(*'X264')
    out = cv2.VideoWriter(filename, fourcc, FRAME_RATE, RESOLUTION)
    return out, filename

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
        camera_records[camera_id]['video_writer'].release()
        return jsonify(success=True)
    return jsonify(success=False, message="Recording not started or already stopped")

@app.route('/video/<int:camera_id>')
def video(camera_id):
    return Response(generate_frames(camera_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('camera_record_test.html')

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
