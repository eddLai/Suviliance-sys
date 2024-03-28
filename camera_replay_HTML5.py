from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = '''
<video id="myVideo" width="640" height="360" loop>
  <source src="/static/videos/t2.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>
<button id="playPauseBtn">Pause</button>
<input type="range" id="progressBar" value="0" max="100">

<style>
#myVideo {
  position: fixed;
  right: 0;
  bottom: 0;
  width: 640px; /* 设置视频的宽度 */
  height: 360px; /* 设置视频的高度 */
}
</style>

<script>
var myVideo = document.getElementById("myVideo");
var playPauseBtn = document.getElementById("playPauseBtn");
var progressBar = document.getElementById("progressBar");

// 播放或暫停视频
playPauseBtn.onclick = function() {
  if (myVideo.paused) {
    myVideo.play();
    playPauseBtn.textContent = "Pause";
  } else {
    myVideo.pause();
    playPauseBtn.textContent = "Play";
  }
};

// 更新进度条
myVideo.ontimeupdate = function() {
  var percentage = Math.floor((100 / myVideo.duration) * myVideo.currentTime);
  progressBar.value = percentage;
};

// 点击进度条来改变视频播放进度
progressBar.addEventListener("input", function() {
  var time = myVideo.duration * (progressBar.value / 100);
  myVideo.currentTime = time;
});

// 初始化进度条最大值
myVideo.onloadedmetadata = function() {
  progressBar.max = myVideo.duration;
};
</script>

'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(debug=True)
