#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Video_speichern.py
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

import numpy as np
import cv2

cap = cv2.VideoCapture(0)

fourcc = cv2.cv.CV_FOURCC('F','M','P','4')
out = cv2.VideoWriter('output2.avi', fourcc, 24.0, (640,480))

while True:
    ret, frame = cap.read()
    if ret==True:
        
        cv2.imshow('frame',frame)
        out.write(frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

cap.release()
out.release()
cv2.destroyAllWindows()
