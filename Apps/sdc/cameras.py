import cv2

num = 0

cameras = []
while 1:
    cap = cv2.VideoCapture(num)
    if cap.isOpened():
        print(cap)
        cameras.append(cap)
        # working capture
        num += 1
    else:
        break


while 1:
    idx = 0
    for cap in cameras:
        retVal, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        canny = cv2.Canny(blur, 50, 150)
        cv2.imshow("Camera  " + str(idx), canny)
        idx = idx + 1

    if cv2.waitKey(1) == ord('q'):
        break

for cap in cameras:
    cap.release()

cv2.destroyAllWindows()