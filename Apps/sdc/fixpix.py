import cv2
import time
import numpy as np

from matplotlib import pyplot as plt

img = cv2.imread('fishpix2.png',0)

blur = cv2.GaussianBlur(img, (5,5), 0)

edges = cv2.Canny(blur,30,200)

plt.subplot(121),plt.imshow(img,cmap = 'gray')
plt.title('Original Image'), plt.xticks([]), plt.yticks([])


plt.subplot(122),plt.imshow(edges,cmap = 'gray')
plt.title('Edge Image'), plt.xticks([]), plt.yticks([])

plt.show()