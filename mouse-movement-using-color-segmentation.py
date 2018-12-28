#!/usr/bin/env python
# coding: utf-8

# In[2]:


#### Cursor Control Using 2 different color strips (RED - Pointer, 1 GREEN - Left click, 2 GREEN - Doube click) #######

import win32api

#Screen Resolution
(sx, sy) = (win32api.GetSystemMetrics(0),win32api.GetSystemMetrics(1))

import cv2
import numpy as np
import time
from pynput.mouse import Button, Controller

#Flag to avoid multiple left clicks when one green stip is being shown
CLICK = 0

mouse = Controller()

#Bounds for the mask
#Red
lowerBound1 = np.array([0, 199, 136])
upperBound1 = np.array([8, 255, 255])
#Green
lowerBound2 = np.array([31, 133, 29])
upperBound2 = np.array([53, 255, 255])

#To reduce noise 
kernelOpen = np.ones((10,10))
kernelClosed = np.ones((15,15))


cam = cv2.VideoCapture(0)
#Set resolution of the webcam
camx, camy = (480, 480)
cam.set(3, camx)  #X axis
cam.set(4, camy)  #Y axis
scaling_factor = round(sx/camx)+1   # To scale from webcam resolution to actual screen resolution

#Store the location of mouse
mouse_prev_loc = np.array([0,0])
mouse_new_loc = np.array([0,0])

dampening_factor = 5 #should be greater than 1


while True:
    #Get image from webcam
    ret, frame = cam.read()
    frame = cv2.flip(frame, 1)
    frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    #Mask for red Strip
    mask = cv2.inRange(frameHSV, lowerBound1, upperBound1)
    maskOpen = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernelOpen)
    maskClosed = cv2.morphologyEx(maskOpen, cv2.MORPH_CLOSE, kernelClosed)
    
    maskFinal1 = maskClosed
    
    #Mask for green strips
    mask = cv2.inRange(frameHSV, lowerBound2, upperBound2)
    maskOpen = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernelOpen)
    maskClosed = cv2.morphologyEx(maskOpen, cv2.MORPH_CLOSE, kernelClosed)
    
    maskFinal2 = maskClosed
    
    #Contours for two colors
    _, contours1, h1 = cv2.findContours(maskFinal1.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    _, contours2, h2 = cv2.findContours(maskFinal2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
    #green strips = 0
    if(len(contours1)!=0 and len(contours2) == 0):
        if(CLICK == 1):
            mouse.release(Button.left)
            CLICK = 0
            
        x,y,w,h = cv2.boundingRect(contours1[0])   
        cv2.circle(frame, (int(x+w/2), int(y+h/2)), 2 , (0,255,0),2)
        cx = (x+w/2)
        cy = (y+h/2)
        
        #To decrease the sensitivity of the mouse (Because hands shake)
        #OR
        #To reduce Mean deviation
        mouse_new_loc = mouse_prev_loc + ((cx, cy) - mouse_prev_loc)/ dampening_factor
        mouse.position = (scaling_factor*(mouse_new_loc[0]-110), scaling_factor*(mouse_new_loc[1]-120))   
        mouse_prev_loc = mouse_new_loc
    
    #green strips = 1
    elif(len(contours1)!=0 and len(contours2) == 1):
        if CLICK == 0:
            mouse.press(Button.left)
            CLICK = 1
            
        x,y,w,h = cv2.boundingRect(contours1[0])
        
        cx = (x+w/2)
        cy = (y+h/2)
        cv2.circle(frame, (int(cx), int(cy)), 2 , (0,255,0),2)
        
        mouse_new_loc = mouse_prev_loc + ((cx, cy) - mouse_prev_loc)/ (dampening_factor + 5) 
        mouse.position = (scaling_factor*(mouse_new_loc[0]-110), scaling_factor*(mouse_new_loc[1]-120))   
        mouse_prev_loc = mouse_new_loc
        
    #green strips = 2
    elif(len(contours1)!=0 and len(contours2) == 2):  
        mouse.click(Button.left, 2)
        time.sleep(1)
    
        
    
    cv2.imshow("mask", frame)
    if(cv2.waitKey(50) == 27):
        break

cam.release()       
cv2.destroyAllWindows()


# In[ ]:




