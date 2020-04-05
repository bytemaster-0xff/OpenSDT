import cv2
import time
import numpy as np


cameras = []

cameras.append(cv2.VideoCapture("http://localhost:9000/cam0.mjpg"))
cameras.append(cv2.VideoCapture("http://localhost:9000/cam1.mjpg"))

face_cascade_name = ".\\data\\haarcascade_frontalface_default.xml"
eyes_cascade_name = ".\\data\\haarcascade_eye_tree_eyeglasses.xml"

face_cascade = cv2.CascadeClassifier()
eyes_cascade = cv2.CascadeClassifier()


#-- 1. Load the cascades
if not face_cascade.load(cv2.samples.findFile(face_cascade_name)):
    print('--(!)Error loading face cascade')
    exit(0)
if not eyes_cascade.load(cv2.samples.findFile(eyes_cascade_name)):
  print('--(!)Error loading eyes cascade')
  exit(0)


def detectAndDisplay(title, frame):
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_gray = cv2.equalizeHist(frame_gray)
    #-- Detect faces
    faces = face_cascade.detectMultiScale(frame_gray)
    for (x,y,w,h) in faces:
        center = (x + w//2, y + h//2)
        frame = cv2.ellipse(frame, center, (w//2, h//2), 0, 0, 360, (255, 0, 255), 4)
        faceROI = frame_gray[y:y+h,x:x+w]
        #-- In each face, detect eyes
        eyes = eyes_cascade.detectMultiScale(faceROI)
        for (x2,y2,w2,h2) in eyes:
            eye_center = (x + x2 + w2//2, y + y2 + h2//2)
            radius = int(round((w2 + h2)*0.25))
            frame = cv2.circle(frame, eye_center, radius, (255, 0, 0 ), 4)
 #   cv2.imshow(title, frame)

while 1:
    try:
        idx = 0
        for camera in cameras:
            retVal, frame = camera.read()
            if(retVal):
                detectAndDisplay("Camera Detect - " + str(idx), frame)
              # gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
               # blur = cv2.GaussianBlur(gray, (5,5), 0)
               # canny = cv2.Canny(blur, 50, 100)
                cv2.imshow("Camera  " + str(idx), frame)
                idx = idx + 1

        if cv2.waitKey(1) == ord('q'):
            break
    except KeyboardInterrupt:
        print("^C received, shutting down.")
        break

for cap in cameras:
    cap.release()

cv2.destroyAllWindows()