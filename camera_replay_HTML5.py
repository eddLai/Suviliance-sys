from flask import Flask, render_template

app = Flask(__name__)

@app.route('/play_video')
def play_video():
    return render_template('video_page.html')

if __name__ == '__main__':
    app.run(debug=True)
