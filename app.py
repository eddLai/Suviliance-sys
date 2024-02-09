from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)

def generate_frames(index):
    camera = cv2.VideoCapture(index)
    while True:
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

if __name__ == '__main__':
    app.run(debug=True)
