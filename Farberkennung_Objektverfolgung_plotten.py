#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Farberkennung_Objektverfolgung_plotten.py
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
from copy import deepcopy
import cPickle as pickle

def plotten3d(daten): #Funktion, welche die Daten plotten kann

	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')

	x_stab = []
	y_stab = []
	z = range(len(daten))

	for i in daten:
		stab_x, stab_y = i
		x_stab.append(stab_x)
		y_stab.append(stab_y)
		
	ax.scatter(x_stab, z, y_stab, c='g', marker='^')
	
	ax.set_xlabel('X-Koordinate')
	ax.set_ylabel('Zeit')
	ax.set_zlabel('Y-Koordinate')
	plt.savefig('3d-Plot.png')
	plt.show()

def color_rec(frame): #Funktion, welche eine nach Farbe definierte Stelle ermittelt

	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)   #konvertiert frame in hsv
	lower = np.array([hue_min, sat_min, val_min])  #legt untere schranke fest
	upper = np.array([hue_max, sat_max, val_max])  # legt obere schranke fest

	#Die Wert aus den Schranken werden aus globalen Variablen gezogen

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

def plotten2d_mit_ableitung(daten, titel):

	
	#verarbeitung der daten
	plt.subplot(2, 1, 1)
	plt.plot(range(len(daten)), daten, 'bo-')
	plt.title('Bewegung und ihre Ableitung im Vergleich ' + titel)
	plt.ylabel('Original-Bewegung ' + titel)
	plt.grid()

	#Ableitung Berechnen
	ableitung = [0]
	for i in range(1,len(daten)):
		ableitung.append(daten[i]-daten[i-1])

	plt.subplot(2, 1, 2)
	plt.plot(range(len(daten)), ableitung, 'r.-')
	plt.xlabel('Zeit (frame)')
	plt.ylabel('Ableitung '+ titel)
	plt.grid()
	plt.savefig("Objektverfolgung_plot1_" + titel + ".png")
	plt.show()	

def schwellenwerte_festlegen(cap):
	erfolgt = False #wurde b schon gedrückt?
	while(erfolgt == False): #Schleife während des Zurechtrückens des Benutzers
		ret, frame = cap.read()
		y_shape, x_shape, z_shape = frame.shape
		zeichne_kreis(frame, (x_shape//2, y_shape//2)) #Kreis wird in der Bildmitte angezeigt
		frame = cv2.flip(frame,1) #Spiegelung des frames an der Horizontalen
		cv2.putText(frame, 'Bitte halten Sie das Objekt hinter der Kreis und druecken Sie dann b.',(5, y_shape-5), 1, 1, (0, 0, 0), 1) #Hinweis für den Benutzer
		cv2.imshow('frame', frame)
		if cv2.waitKey(1) & 0xFF == ord('b'): #Signal, dass in Position, über das Drücken von b
			break

	ret, frame = cap.read() #frame ohne Kreis wird geholt
	zu_unt = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) #Konvertierung in hsv
	radius = 25 #Radius des zu untersuchenden Kreises
	liste_kreisinhalt = [] #diese Liste soll alle Pixel enthalten, die innerhalb des Kreises liegen
	for i in range(x_shape): #das Bild wird pixelweise durchgegangen. Wenn der Pixel im Bild liegt, wir dieser registriert
		for j in range(y_shape):
			if np.sqrt((x_shape//2-i)**2+(y_shape//2-j)**2) < radius: #Hier Satz des Pythagoras zur Entfernungsbestimmung Pixel--Kreismittelpunkt
				liste_kreisinhalt.append(zu_unt[j][i])
	array_kreisinhalt = np.array(liste_kreisinhalt) #Konvertierung in Array zur weiteren Verarbeitung

	hue = array_kreisinhalt[:,0] #Liste mit allen hue-Werten wird angelegt
	sat = array_kreisinhalt[:,1] #Liste mit allen sat-Werten wird angelegt
	val = array_kreisinhalt[:,2] #Liste mit allen val-Werten wird angelegt

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
	output.close() #der Output wird geschlossenr

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
	
###============Beginn eigentliches Programm===================###

def main():


	schwellenwerte_einlesen() #Schwellenwerte werden zu beginn festgelegt (für hsv)

	global position #Variable, welche die Frames durchläuft
	position = 0

	cap = cv2.VideoCapture(0) #Angeschlossene Kamera wird geöffnet

	cap.set(3,640)
	cap.set(4,480)
	#cap.set(15, 0.1)

	ret, frame = cap.read() #Erster Frame wird abgerufen
	y_shape, x_shape, z_shape = frame.shape #Videomaße für den Kopfentwicklungspunkt werden ausgelesen


	global stab #Liste der Taktstockpositionen
	stab_x = []
	stab_y = []
	stab = []

	while(True):
	
		ret, frame = cap.read() #Holt Frame
		frame = cv2.flip(frame,1)
		if position < 120: #Benutzerinstruktionen in den ersten 120 frames
			cv2.putText(frame, 'zum kalibrieren s druecken und zum beenden q.', (5, y_shape - 5), 1,1, (0, 0, 0), 1)
		position +=1 #Framenummer wird um 1 erhöht
		
		stab_position = color_rec(frame)
		stab.append(stab_position)
		x_position_stab, y_position_stab = stab_position
		stab_x.append(x_position_stab)
		stab_y.append(y_position_stab)
		zeichne_kreis(frame,stab_position) #Kreis wird an aktueller Taktstockposition gezeichnet
		
		
		cv2.imshow('frame',frame) #Ergebnis wird angezeigt
		
		if cv2.waitKey(1) & 0xFF == ord('q'): #'q' zum Beenden drücken
			break
		if cv2.waitKey(1) & 0xFF == ord('s'):  #Schwellenwerte festlegen
			schwellenwerte_festlegen(cap)

	plotten3d(stab) #die Daten werden geplottet
	plotten2d_mit_ableitung(stab_x, "X-Bewegung")
	plotten2d_mit_ableitung(stab_y, "Y-Bewegung")

	cap.release()
	cv2.destroyAllWindows()
	#THE ENDE

if __name__ == "__main__":
	main()
