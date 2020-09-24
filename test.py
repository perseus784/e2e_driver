import os
import cv2


gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, th=cv2.threshold(gray,140,250,cv2.THRESH_BINARY)
gaussian=cv2.GaussianBlur(th,(3,3),0)#smoothening
edges = cv2.Canny(gaussian,1000,200,apertureSize =5)# edge detection
lines = cv2.HoughLinesP(edges,1,np.pi/180,50,40,10) #hough probalistic
try:
    for line in lines:
        x1,y1,x2,y2=line[0]
        cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)
except:pass