# https://www.udemy.com/course/applied-deep-learningtm-the-complete-self-driving-car-course/learn/lecture/11241784#overview

import cv2
import numpy as np
import matplotlib.pyplot as plt
from numpy.polynomial.polynomial import polyval

last_left_line = [0,0,0,0]
last_right_line = [0,0,0,0]

left_slope_buffer = []
right_slope_buffer = []
lane_width_buffer = []

last_center = 640

left = 290
right = 800
top = 150

bottom_margin = 150
x_top_offset = 60
last_center = 400


def make_coordinates(image, line_parameters):
    slope, intercept = line_parameters
    y1 = image.shape[0] - bottom_margin
    y2 = y1 - top
    x1 = int((y1 - intercept) / slope)
    x2 = int((y2 - intercept) / slope)
    
    return np.array([x1, y1, x2, y2])

def average_slope_intercept(image, lines, last_center):
    global last_left_line
    global last_right_line

    if(lines is None or len(lines) == 0):
        return np.array([last_left_line, last_right_line])

    left_fit = []
    right_fit = []

    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)


        parameters = np.polyfit((x1, x2), (y1, y2), 1)
        #parameters = polyval((x1, x2), (y1, y2), 1)
        slope = parameters[0]
        intercept = parameters[1]
        if slope < -0.5:
            left_fit.append((slope, intercept))
        elif slope > 0.5:
            right_fit.append((slope, intercept))

    global left_slope_buffer
    global right_slope_buffer

    if(len(left_fit) == 0):
        left_line = last_left_line
    else:
        left_fit_average = np.average(left_fit, axis = 0)
        left_slope_buffer.append(left_fit_average)
        left_fit_average = np.average(left_slope_buffer, axis=0)
        if(len(left_slope_buffer) > 30):
            left_slope_buffer.pop(0)

        left_line = make_coordinates(image, left_fit_average)
        last_left_line = left_line

    if(len(right_fit) == 0):
        right_line = last_right_line
    else:
        right_fit_average = np.average(right_fit, axis = 0)
        right_slope_buffer.append(right_fit_average)
        right_fit_average = np.average(right_slope_buffer, axis = 0)
        if(len(right_slope_buffer) > 30):
            right_slope_buffer.pop(0)
        
        right_line = make_coordinates(image, right_fit_average)
        last_right_line = right_line

    this_lane_width = right_line[0] - left_line[0]

    lane_width_buffer.append(this_lane_width)
    lane_width_avg = np.average(lane_width_buffer, axis=0)
    
    if(len(lane_width_buffer) > 30):
        lane_width_buffer.pop(0)

    delta = int((lane_width_avg - this_lane_width) / 2)

    left_line = np.array([left_line[0] - delta, left_line[1], left_line[2], left_line[3]])
    right_line = np.array([right_line[0] + delta, right_line[1], right_line[2], right_line[3]])
    
    return np.array([left_line, right_line])

def display_lines(image, lines):
    line_image = np.zeros_like(image)
    if lines is not None:
        for x1, y1, x2, y2 in lines:
            cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 5)
            
    return line_image

def display_region(image, lines):
    line_image = np.zeros_like(image)
    if lines is not None and len(lines) > 1:
        if(len(lines[0]) > 3 and len(lines[1] > 3)):
            x11, y11, x12, y12 = lines[0].reshape(4)
            x21, y21, x22, y22 = lines[1].reshape(4)
                    
            polygons = np.array([[
                [x11, y11], [x21, y21],
                [x22, y22], [x12, y12]]])

            cv2.fillPoly(line_image, polygons, (0,255, 0))

    return line_image
        
def display_all_lines(image, lines):
    line_image = np.zeros_like(image)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            parameters = np.polyfit((x1, x2), (y1, y2), 1)
            slope = parameters[0]
            if(slope > 0.5 or slope < -0.5):
                cv2.line(line_image, (x1, y1), (x2, y2), (0, 0, 255), 5)
            
    return line_image

def detect_cars(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    cars = car_cascade.detectMultiScale(gray, 1.5, 2)     
    for (x, y, w, h) in cars:
        cv2.rectangle(image, (x,y), (x+w,y+h), (0,0,255), 2)

def canny(image):
   # gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(image, (5,5), 0)
    canny = cv2.Canny(blur, 50, 150)
    return canny
    
def region_of_interest(image, left, right, top, center, bottom_margin, x_top_offset):
    bottom = image.shape[0] - bottom_margin
    center = last_center

    height = bottom - top
    polygons = np.array([
            [(left, bottom), (right, bottom), (center + x_top_offset, height), (center - x_top_offset, height)]
        ])
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, polygons, (255, 255, 255))
    masked_image = cv2.bitwise_and(image, mask)
    return masked_image

car_cascade = cv2.CascadeClassifier('.\\data\\cars.xml')
cap = cv2.VideoCapture("s:\Titan_2020_05_07.mp4")

cross_y = 100
cross_diameter = 30

while(cap.isOpened()):
    try:
        ret, frame = cap.read()
        if(ret):
            detect_cars(frame)
             
            canny_image = canny(cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY))
     
            cropped_image = region_of_interest(canny_image, left, right, top, last_center, bottom_margin, x_top_offset)
       
            lines = cv2.HoughLinesP(cropped_image, 2, np.pi / 180, 40, np.array([]), minLineLength=5, maxLineGap=2)
            averaged_lines = average_slope_intercept(frame, lines, last_center)
            avg_line_image = display_region(frame, averaged_lines)

            print(averaged_lines)
            if(averaged_lines[0][2] < averaged_lines[1][2]):
                line_image = display_all_lines(frame, lines)
                averageX = int((averaged_lines[0][2] + averaged_lines[1][2]) / 2)
                last_center = averageX

                combo_image = cv2.addWeighted(avg_line_image, 0.25, frame, 1, 1)
                combo_image = cv2.addWeighted(line_image, 0.98, combo_image, 1, 1)
                cv2.line(combo_image, (averageX, cross_y + cross_diameter), (averageX, cross_y - cross_diameter), (0, 0, 255), 2)
                cv2.line(combo_image, (averageX - cross_diameter, cross_y), (averageX + cross_diameter, cross_y), (0, 0, 255), 2)
                cv2.imshow('Result', combo_image  )
            else:
                cv2.imshow('Result', frame )
          
        else:
            print("End of Video")
            break
        if cv2.waitKey(1) == ord('q'):
            break
    
    except KeyboardInterrupt:
        print("^C received, shutting down.")
        break

cap.release()
cv2.destroyAllWindows()

