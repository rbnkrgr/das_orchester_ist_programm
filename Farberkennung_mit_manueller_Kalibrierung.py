#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Farberkennung_mit_manueller_Kalibrierung.py
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
import numpy as np
import cv2
import time

def zeichne_rechteck(frame,position,farbe,dicke=2):
	x, y = position
	cv2.rectangle(frame, (x-20, y-20), (x+20, y+20), farbe, dicke)

cap = cv2.VideoCapture(0)

while True:
	_, frame = cap.read()

	
	hue_low = 160 #0-360
	hue_up  = 190 #0-360
	sat_low = 60  #0-100
	sat_up  = 105 #0-100
	val_low = 30  #0-100
	val_up  = 55  #0-100
	
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)						#konvertiert frame in hsv 
	lower = np.array([hue_low/2,255*sat_low/100,255*val_low/100])		#legt untere schranke fest (hier für pinke schere)
	upper = np.array([hue_up/2,255*sat_up/100,255*val_up/100])			#legt obere schranke fest
	mask =  cv2.inRange(hsv, lower, upper)								#erstellt maske, welche für werte innerhalb des intervalls
																		#den wert 1 annimmt, sonst 0
	y_werte, x_werte = np.where(mask == 255)
	y_mittel = np.sum(y_werte)//(len(y_werte)+1)
	x_mittel = np.sum(x_werte)//(len(x_werte)+1)
	position = (x_mittel, y_mittel)

	if position == (0,0):
		x_shape, y_shape, _ = frame.shape
		position = (x_shape//2,y_shape//2)

	cv2.circle(frame,position, 25, (0,0,255),4)    
	
	cv2.imshow("frame", frame)

	
	if cv2.waitKey(1) & 0xFF == ord(' '):
		break	

cap.release()
cv2.destroyAllWindows()
