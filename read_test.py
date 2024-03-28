import cv2

# 設定MP4檔案的路徑
video_path = 'D:\\testforstreaming\\output.mp4'

# 創建VideoCapture物件並讀取視頻檔案
cap = cv2.VideoCapture(video_path)

# 檢查視頻是否成功開啟
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# 逐幀讀取視頻
while True:
    # 讀取當前幀
    ret, frame = cap.read()

    # 如果成功讀取到幀，ret是True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    # 顯示幀
    cv2.imshow('Frame', frame)

    # 按下 'q' 鍵退出迴圈
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

# 釋放VideoCapture物件
cap.release()
# 關閉所有OpenCV視窗
cv2.destroyAllWindows()
