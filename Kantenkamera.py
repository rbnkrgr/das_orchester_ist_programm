#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Kantenkamera.py
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

cap = cv2.VideoCapture(0)

while(True):
	ret, frame = cap.read()							#.read liefert tupel zurück: ret ist False wenn es einen Fehler gibt
													# und hinter frame verbirgt sich ein numpy-array des eingelesenen bildes
	lo=frame[:-1,:-1,:1]							#slicing für die 3d matrix des frames
	ro=frame[:-1,1:,:1]
	lu=frame[1:,:-1,:1]
	ru=frame[1:,1:,:1]

	dif1=np.absolute(lo-ru)							#absolutbetrag der differenzen obiger verschobener bilder
	dif2=np.absolute(ro-lu)							#links steht im prinzip mein code für die kanten-aufgabe
	dif3=np.absolute(lo-ro)							#leider kann ich keine schwellenwerte definieren
	dif4=np.absolute(lu-ru)
	dif5=np.absolute(lo-lu)
	dif6=np.absolute(ro-ru)
	ges=dif1+dif2+dif3+dif4+dif5+dif6
	
	cv2.imshow("frame", ges)						#imshow(name des fensters, anzuzeigendes bild)

	if cv2.waitKey(1) & 0xFF == ord(' '):			#falls 8bit information der gedrückten Taste mit ord() übereinstimmt --> break
		break

cap.release()
cv2.destroyAllWindows()

