#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Optischer_Fluss.py
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

import cv2
import numpy as np
#Webcam wird angeschaltet
cap = cv2.VideoCapture(0)
#Codierung d. Videos und outputfile
fourcc = cv2.cv.CV_FOURCC('F','M','P','4')
out = cv2.VideoWriter('bunt.avi', fourcc, 24.0, (640,480))

#erstes Bild wird eingelesen; grau; 
ret, frame1 = cap.read()
prvs = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)

#erstell mit Nullen gefuelltes array, gleiche Groesse wie frame1
hsv = np.zeros_like(frame1)
hsv[...,1] = 255

while True:
	#zweites Bild wird eingelesen
    ret, frame2 = cap.read()
    next = cv2.cvtColor(frame2,cv2.COLOR_BGR2GRAY)
	#berechnet optischen Fluss mit Farnebackmethode
    flow = cv2.calcOpticalFlowFarneback(prvs,next, 0.5, 3, 15, 3, 5, 1.2, 0)
	#berechnet groesse und winkel von flow und flow
    mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
    hsv[...,0] = ang*180/np.pi/2
    hsv[...,2] = cv2.normalize(mag,None,0,255,cv2.NORM_MINMAX)
    rgb = cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)

    cv2.imshow('frame2',rgb)
    out.write(rgb)
    k = cv2.waitKey(30) & 0xff
    if k == ord('q'):
        cv2.imwrite('opticalfb.png',frame2)
        cv2.imwrite('opticalhsv.png',rgb)
        break

    prvs = next

cap.release()
out.release()
cv2.destroyAllWindows()
