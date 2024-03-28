import cv2
import sys

def find_available_cameras(max_checks=10):
    """
    探測可用的攝像頭。
    :param max_checks: 最大探測索引數
    :return: 可用攝像頭的索引列表
    """
    available_cameras = []
    for index in range(max_checks):
        cap = None
        try:
            # 嘗試使用DirectShow（僅限Windows）
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            if not cap.isOpened():
                # 如果DirectShow不可用，嘗試不指定後端
                cap.open(index)
            if cap.isOpened():
                print(f"Camera found at index {index}")
                available_cameras.append(index)
        except cv2.error as e:
            print(f"Error opening camera at index {index}: {e}")
        finally:
            if cap is not None:
                cap.release()
    return available_cameras

def test_camera(index):
    """
    測試給定索引的攝像頭。
    :param index: 攝像頭索引
    """
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print(f"Failed to open camera at index {index}")
        return
    
    print(f"Successfully opened camera at index {index}. Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        cv2.imshow(f"Camera {index}", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    cameras = find_available_cameras()
    if cameras:
        print(f"Available cameras: {cameras}")
        for cam_index in cameras:
            test_camera(cam_index)
    else:
        print("No cameras found.")


