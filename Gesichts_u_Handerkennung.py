#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Gesichts_u_Handerkennung.py
#  
#  This program was created as part of the laboratory Mathesis at the Technical University Berlin .
#  Copyright 2016 Henriette Behr, Henriette Rilling, Max Wehner, Robin Krueger <das_orchester_ist_programm@web.de>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

from __future__ import division
from scipy import misc, ndimage
from mpl_toolkits.mplot3d import Axes3D
import math as m
import random
import time
import matplotlib.pyplot as plt
import numpy as np
import cv2
import sys

faceCascade = cv2.CascadeClassifier("face.xml")
handCascade = cv2.CascadeClassifier("hand.xml")
fi=0

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.cv.CV_HAAR_SCALE_IMAGE
    )
    
    hands = handCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.cv.CV_HAAR_SCALE_IMAGE
    )

    if fi%4==0:
		for (x, y, w, h) in faces:
			cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
			xcf=(x+w//2)
			ycf=(y+h//2)
			print "f:", xcf, ycf
    else:
		pass
		
    fi+=1

    for (x, y, w, h) in hands:
		cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
		xch=(x+w//2)
		ych=(y+h//2)
		print "h:", xch, ych

    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord(' '):
        break

cap.release()
cv2.destroyAllWindows()
