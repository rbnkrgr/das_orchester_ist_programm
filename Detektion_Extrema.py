#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Detektion_Extrema.py
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

def plotten3d_gesamt(daten): #Funktion, welche die Daten plotten kann

	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')

	x_head = []
	y_head = []
	x_stab = []
	y_stab = []
	z = range(len(daten))

	for i in daten:
		head_x, head_y, stab_x, stab_y = i
		x_head.append(head_x)
		y_head.append(head_y)
		x_stab.append(stab_x)
		y_stab.append(stab_y)
		
	ax.scatter(x_head, z, y_head, c='b', marker='x')
	ax.scatter(x_stab, z, y_stab, c='g', marker='^')
	
	ax.set_xlabel('X-Koordinate')
	ax.set_ylabel('Zeit')
	ax.set_zlabel('Y-Koordinate')

	plt.show()

def face_rec(cascade, bild): #Funktion, welch Gesichter erkennt und sich für eines entscheidet

	gray = cv2.cvtColor(bild, cv2.COLOR_BGR2GRAY) #Konvertierung nach Grau

	faces = cascade.detectMultiScale(
		gray,
		scaleFactor=1.1,
		minNeighbors=5,
		minSize=(60, 60),
		flags=cv2.cv.CV_HAAR_SCALE_IMAGE)
	temp = []
	x_old, y_old, w_old, h_old = head[position-1]
	for i in range(len(faces)):
		x_new, y_new, w_new, h_new = list(faces[i])
		temp.append(np.sqrt(x_old*x_new+y_old*y_new))
	if temp == []:
		comp_position = head[position]
	elif min(temp) < 300:
		comp_position = faces[temp.index(min(temp))]
	else:
		comp_position = head[position]
	
	return comp_position

def zeichne_rechteck(frame, position, farbe, dicke=2): #Funktion, welche ein Rechteck zeichnet
	x, y, w, h = position
	cv2.rectangle(frame, (x, y), (x+w, y+h), farbe, dicke)

def color_rec(frame): #Funktion, welche eine nach Farbe definierte Stelle ermittelt
	
	#     -> Die Werte können nun wie im Zeichenprogramm (z.B. GIMP) gewählt werden
	hue_low = 95 #0-360
	hue_up  = 120 #0-360
	sat_low = 50  #0-100
	sat_up  = 75 #0-100
	val_low = 30  #0-100
	val_up  = 75  #0-100      -> Hier eingestellt für grünen Stift
	
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)						#konvertiert frame in hsv 
	lower = np.array([hue_low/2,255*sat_low/100,255*val_low/100])		#legt untere schranke fest
	upper = np.array([hue_up/2,255*sat_up/100,255*val_up/100])			#legt obere schranke fest
	mask =  cv2.inRange(hsv, lower, upper)								#erstellt maske, welche für werte innerhalb des intervalls
																		#den wert 1 annimmt, sonst 0
	y_werte, x_werte = np.where(mask == 255)							#Es werden die x- und y-Werte ausgelesen, welche ein True (255) bekomen haben
	if len(x_werte) != 0 and len(y_werte) != 0:
		y_mittel = int(np.mean(y_werte))									#Es wird der Mittelwert aus allen y-Werten gebildet
		x_mittel = int(np.mean(x_werte))									#Es wird der Mittelwert aus allen x-Werten gebildet
		position = (x_mittel, y_mittel)										#Die Mittlere Position aller Trues entspricht dem Tupel beider Mittelwerte

	else:
		position = (0,0)

	if position == (0,0):												#Sollten keine Trues gefunden werden (Gesamtmittelwert = (0,0))
		x_shape, y_shape, _ = frame.shape								#Es werden die Bildmaße ausgelesen
		position = (x_shape//2,y_shape//2)								#Als Position wird der Bildmittelpunkt gewählt

	return position														#Ergebnis wird zurückgegeben

def zeichne_kreis(frame, position): #Funktion, welche einen Kreis zeichnet
	cv2.circle(frame,position, 25, (0,0,255), 4)   

def plotten2d_ableitung(daten, art, ableitung):
	ableitung.append(0)
	#daten entpacken
	x_head = []
	y_head = []
	x_stab = []
	y_stab = []
	z = range(len(daten))

	for i in daten:
		head_x, head_y, stab_x, stab_y = i
		x_head.append(head_x)
		y_head.append(head_y)
		x_stab.append(stab_x)
		y_stab.append(stab_y)
	
	#verarbeitung der daten
	
	auswahl = [x_head, y_head, x_stab, y_stab]
	auswahl_text = ['Kopf-X','Kopf-Y','Stab-X','Stab-Y']
	
	x1 = auswahl[art]
	x2 = ableitung

	y1 = z
	y2 = z

	plt.subplot(2, 1, 1)
	plt.plot(y1, x1, 'bo-')
	plt.title('Bewegung und ihre Ableitung im Vergleich ' + auswahl_text[art])
	plt.ylabel('Original-Bewegung ' + auswahl_text[art])
	plt.grid()

	plt.subplot(2, 1, 2)
	plt.plot(y2, x2, 'r.-')
	plt.xlabel('Zeit (frame)')
	plt.ylabel('Ableitung '+ auswahl_text[art])
	plt.grid()

	plt.show()	
			
faceCascade = cv2.CascadeClassifier("face.xml") #Cascade fürs Gesicht wird geladen

global position #Variable, welche die Frames durchläuft
position = 0

cap = cv2.VideoCapture(0) #Angeschlossene Kamera wird geöffnet

ret, frame = cap.read() #Erster Frame wird abgerufen
y_shape, x_shape, z_shape = frame.shape #Videomaße für den Kopfentwicklungspunkt werden ausgelesen

global head #Liste der Kopfpositionen
head=[(x_shape//2,0,0,0)] #Entwicklungspunkt für den Kopf

global stab #Liste der Taktstockpositionen
stab = []

global daten #Liste der wichtigsten Daten
daten = []

dx_nach_dt = [0]

dy_nach_dt = [0]

while(True):
	ret, frame = cap.read() #Holt Frame

	head.append(face_rec(faceCascade,frame)) #Ermittelte Kopfposition wird registriert (mit Hoehe und Breite)
	zeichne_rechteck(frame,head[position],(255,0,0),2) #Rechteck wird an aktueller Kopfposition gezeichnet

	stab.append(color_rec(frame)) #Ermittelte Taktstockposition wird registriert
	zeichne_kreis(frame,stab[position]) #Kreis wird an aktueller Taktstockposition gezeichnet
	
	head_x, head_y,_,_ = head[position] #die 'wichtigen' Daten (die aktuelle Position) werden aus der Kopfposition extrahiert
	stab_x, stab_y = stab[position-1] #die aktuellen Daten werden aus der Taktstockposition extrahiert
	daten.append((head_x, head_y, stab_x, stab_y)) #die extrahierten Daten werden zur weiteren verarbeitung gespeichert
	
	if position > 1: #Ableitungen bestimmen
		stab_x_old, stab_y_old = stab[position-2]
		dx_nach_dt.append(stab_x_old-stab_x)
		dy_nach_dt.append(stab_y_old-stab_y)
		
		if dx_nach_dt[position-1] > 0 and dx_nach_dt[position-2] <= 0:
			cv2.circle(frame, (x_shape-20,y_shape//2), 10, (255,0,0),10)
			
		if dx_nach_dt[position-1] < 0 and dx_nach_dt[position-2] >= 0:
			cv2.circle(frame, (20,y_shape//2), 10, (255,0,0),10)
			
		if dy_nach_dt[position-1] > 0 and dy_nach_dt[position-2] <= 0:
			cv2.circle(frame, (x_shape//2,y_shape-20), 10, (255,0,0),10)
			
		if dy_nach_dt[position-1] < 0 and dy_nach_dt[position-2] >= 0:
			cv2.circle(frame, (x_shape//2,20), 10, (255,0,0),10)

			
	
	position +=1 #Framenummer wird um 1 erhöht
	cv2.imshow('frame',cv2.flip(frame,1)) #Ergebnis wird angezeigt
	if cv2.waitKey(1) & 0xFF == ord('q'): #'q' zum Beenden drücken
		break

plotten3d_gesamt(daten) #die Daten werden geplottet
plotten2d_ableitung(daten, 2, dx_nach_dt)
plotten2d_ableitung(daten, 3, dy_nach_dt)

cap.release()
cv2.destroyAllWindows()
#THE ENDE
