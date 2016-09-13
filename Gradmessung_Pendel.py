#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Gradmessung_Pendel.py
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
import time
import numpy as np
import cv2
import pickle

def get_visual(ref, pos):
	mittelpunkt = ref
	radius = 150
	mittelpunkt_x, mittelpunkt_y = mittelpunkt
	links_oben = (mittelpunkt_x-radius, mittelpunkt_y)
	rechts_oben = (mittelpunkt_x+radius, mittelpunkt_y)
	
	position_x, position_y = position
	
	cv2.line(frame, ref, pos, (0,255,0), 2)
	cv2.line(frame, (0,mittelpunkt_y), (640,mittelpunkt_y), (255,255,0), 2)
	cv2.circle(frame, pos, 4, (0,0,255), -1)	
	cv2.circle(frame, ref, 4, (0,0,255), -1)
	cv2.circle(frame, ref, cthresh, (0,255,0), 2)

	entfernung = np.sqrt((mittelpunkt_x-position_x)**2+(position_y-mittelpunkt_y)**2)
	
	for x in range(2*radius): #x-Werte durchgehen
		for y in range(radius):
			links_oben_x, links_oben_y = links_oben
			rechts_oben_x, rechts_oben_y = rechts_oben
			x_pos = links_oben_x+x
			y_pos = links_oben_y+y

			auslenkung = (position_x-mittelpunkt_x)*radius/entfernung
			if (radius-1)**2 < (mittelpunkt_x-x_pos)**2+(mittelpunkt_y-y_pos)**2 < (radius+1)**2:
				if (x_pos-mittelpunkt_x) < auslenkung:
					cv2.circle(frame, (x_pos,y_pos), 1, (0,0,255), -1)
					
	try:
		winkel = np.degrees(np.arctan((mittelpunkt_x-position_x)/(-mittelpunkt_y+position_y))) +90
		return winkel
	except:
		return 0
	
def detect_color(frame): #Funktion, welche eine nach Farbe definierte Stelle ermittelt

	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)   #konvertiert frame in hsv
	lower = np.array([hue_min, sat_min, val_min])  #legt untere schranke fest
	upper = np.array([hue_max, sat_max, val_max])  #legt obere schranke fest

	#Die Wert aus den Schranken werden aus globalen Variablen gezogen

	mask =  cv2.inRange(hsv, lower, upper)								#erstellt maske, welche für werte innerhalb des intervalls
																		#den wert 1 annimmt, sonst 0
	y_werte, x_werte = np.where(mask == 255)							#Es werden die x- und y-Werte ausgelesen, welche ein True (255) bekomen haben
	if len(x_werte) > 20:												###es reicht eine bedingung zu erfüllen + schwellenwert
		y_mittel = int(np.mean(y_werte))								#Es wird der Mittelwert aus allen y-Werten gebildet
		x_mittel = int(np.mean(x_werte))								#Es wird der Mittelwert aus allen x-Werten gebildet
		position = (x_mittel, y_mittel)									#Die Mittlere Position aller Trues entspricht dem Tupel beider Mittelwerte

	else:																###if-bedingung unnötig, mittelpunkt erhält man durch tausch von x und y
		y_shape, x_shape, _ = frame.shape								#Es werden die Bildmaße ausgelesen
		position = (int(x_shape//2),int(y_shape//2))					#Als Position wird der Bildmittelpunkt gewählt
		
	return position														#Ergebnis wird zurückgegeben
	
def schwellenwerte_einlesen():
	global hue_min #die Schwellenwerte werden als global definiert
	global hue_max
	global sat_min
	global sat_max
	global val_min
	global val_max

	try: #es wird versucht / festgestellt, ob es bereits eine Datei mit gespeicherten Schwellenwerten gibt
		f = open("hsv_werte.pkl") #falls ja wird diese geoeffnet
		sicherung = pickle.load(f)
		hue_min, hue_max, sat_min, sat_max, val_min, val_max = sicherung #und die Daten entpackt

	except: #falls nein, werden sehr komische Werte festgelegt, damit der Benutzter das Programm kalibriert
		val_max = 1
		val_min = 0
		sat_max = 1
		sat_min = 0
		hue_max = 1
		hue_min = 0
	
def get_values(cap):
	while(True): 
		_, frame = cap.read()
		y_shape, x_shape, _ = frame.shape
		cv2.circle(frame,(x_shape//2, y_shape//2),25,(0,0,255),4)
		frame = cv2.flip(frame,1) #Spiegelung des frames an der Horizontalen
		cv2.putText(frame, "Bereit? [B]", (200,450), 2, 1, (255,255,255), 0)
		cv2.imshow('frame', frame)
		if cv2.waitKey(1) & 0xFF == ord('b'): #Signal, dass in Position, über das Drücken von k
			break
		if cv2.waitKey(1) & 0xFF == ord(' '): 
			cap.release()
			sys.exit()

	ret, frame = cap.read() #frame ohne Kreis wird geholt
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) #Konvertierung in hsv
	radius = 25 #Radius des zu untersuchenden Kreises
	kreisliste = [] #diese Liste soll alle Pixel enthalten, die innerhalb des Kreises liegen
	for i in range(x_shape): #das Bild wird pixelweise durchgegangen. Wenn der Pixel im Bild liegt, wir dieser registriert
		for j in range(y_shape):
			if np.sqrt((x_shape//2-i)**2+(y_shape//2-j)**2) < radius: #Hier Satz des Pythagoras zur Entfernungsbestimmung Pixel--Kreismittelpunkt
				kreisliste.append(hsv[j][i])
	npkreisliste = np.array(kreisliste) #Konvertierung in Array zur weiteren Verarbeitung

	hue = npkreisliste[:,0] #Array mit allen hue-Werten wird angelegt
	sat = npkreisliste[:,1] #Array mit allen sat-Werten wird angelegt
	val = npkreisliste[:,2] #Array mit allen val-Werten wird angelegt

		#Berechung der Grenzen erfolgt, wie folgt. Zuerst wird der Mittelwert aller Werte einer Eigenschaft gebildet.
		#Als nächstes wird jeweils die Standartabweichung ermittelt.
		#Die untere Schranke ist dann einfach der Mittelwert - die Standartabweichun
		#Die obere Schranke ist einfach der Mittelwert + die Standartabweichung.

		#Die Ergebnisse werden zur direkten Weiterverwendung in globale Variablen geschrieben.
		#Zur verwendung nach einem Programmneustart werden sie in eine datei ausgelagert.

	global hue_min #globale Variable wird angelegt
	hue_min = int(np.mean(hue) - np.std(hue)) #Wert wird ermittelt
	global hue_max
	hue_max = int(np.mean(hue) + np.std(hue))
	global sat_min
	sat_min = int(np.mean(sat) - np.std(sat))
	global sat_max
	sat_max = int(np.mean(sat) + np.std(sat))
	global val_min
	val_min = int(np.mean(val) - np.std(val))
	global val_max
	val_max = int(np.mean(val) + np.std(val))
	
	sicherung = (hue_min,hue_max,sat_min,sat_max,val_min,val_max) #erzeuge Datensatztupel zur Abspeicherung für Pickle
	output = open('hsv_werte.pkl', 'w') #die Ausgabedatei wird vorbereitet
	pickle.dump(sicherung, output) #die Daten werden geschrieben
	output.close() #der Output wird geschlossen
	
#=======thresholds=======#

cthresh = 30			#radius des toleranzkreises

#=======program=======#

cap = cv2.VideoCapture(0)

schwellenwerte_einlesen()
ref = (320,100)

schwellenwerte_einlesen()

while True:
	_, frame = cap.read()	

	position = detect_color(frame)

	winkel = get_visual(ref, position)	

	frame = cv2.flip(frame,1)
	
	cv2.putText(frame, str(round(winkel,3)), (520,40), 2, 1, (255,255,255), 0)
	
	cv2.imshow("frame", frame)

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break	
	if cv2.waitKey(1) & 0xFF == ord('k'):
		get_values(cap)


cap.release()
cv2.destroyAllWindows()
