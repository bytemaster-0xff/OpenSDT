import cv2
import numpy as np
import matplotlib.pyplot as plt

cap = cv2.VideoCapture("s:\Titan_2020_05_07.mp4")

ret, frame = cap.read()

combo_image = frame


height=180

left = 150
right = 700
top = 150

bottom_margin = 150
x_top_offset = 20
last_center = 320

center = 500
bottom = 330

top = bottom - height

polygons = np.array([
            [(left, bottom), (right, bottom), (center + x_top_offset, top), (center - x_top_offset, top)]
        ])
mask = np.zeros_like(frame)

cv2.fillPoly(frame, polygons, (255, 255, 255))

cv2.imshow('Result', frame)


  
cv2.waitKey(0)