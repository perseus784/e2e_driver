import os
import cv2
import numpy as np

cap = cv2.VideoCapture("man360grey.avi")
kernel = np.ones((2, 1), np.uint8)

while cap.isOpened():
    ret, frame = cap.read()
    if ret == True:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, th = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY)
        opening = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)
        blurred = cv2.medianBlur(opening, 1) #smoothening
        edges = cv2.Canny(blurred, 10, 250, apertureSize = 7)# edge detection
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 15, 100, 1) #hough probalistic
        try:
            for line in lines:
                x1, y1, x2, y2=line[0]
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        except:
            pass

        #cv2.imshow("gray", gray)
        #cv2.imshow("theshold", th)
        cv2.imshow("opening", opening)
        cv2.imshow("gaussian", blurred)
        cv2.imshow("edges", edges)
        cv2.imshow("live", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break    

cap.release()
cv2.destroyAllWindows()


