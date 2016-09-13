# -*- encoding: utf-8 -*-
# Technische Universität Berlin
# mathematisch-naturwissenschaftliches Labor Mathesis
# die 'Dirigieren'-Gruppe

from __future__ import division
from scipy import misc, ndimage
from mpl_toolkits.mplot3d import Axes3D
import math as m
import random
import time
#from time import *
import matplotlib.pyplot as plt
import numpy as np
import cv2
import sys
from copy import deepcopy
import pickle
import turtle as turtle

def figur_finden(zu_untersuchen, figur): #diese Funktion versucht Figuren im Dirigat zu erkennen. Dafuer bekommt sie die Figurvektoren in richtiger Reihenfolge, sowie die Liste mit den dirigierten Vektoren uebergeben
	figurlaenge = len(figur)
	
	zu_untersuchen_kurz = [] #Diese Liste soll die letzten dirigierten Vektoren enthalten, die wichtig sind
	for i in range(figurlaenge,0,-1):
		zu_untersuchen_kurz.append(zu_untersuchen[-i]) #letzten Eintraege werden ermittelt
	zu_untersuchen_kurz = np.array(zu_untersuchen_kurz) #zur weiteren Verarbeitung Konvertierung in Array
		
	figurensammlung = [] #verschiedene Kombinationen werden angelegt, schwierig sich das ohne zeichnung vorzustellen. Bsp.: aus [1,2,3] wird [[1,2,3],[2,3,1],[3,2,1]]
	tmp = figur
	for i in range(figurlaenge):
		tmp.append(tmp[0])
		del(tmp[0])
		anhaengen = deepcopy(tmp)
		figurensammlung.append(anhaengen)
	figurensammlung = np.array(figurensammlung) #zur weiteren Verarbeitung Konvertierung in Array

	for i in range(figurlaenge): #Der Vergleich findet statt
		if np.array_equiv(figurensammlung[i],zu_untersuchen_kurz): #elementweises Vergleichen von letztem Dirigat und verschiedenen Figur-Kombinationen
			return True #falls Figur gefunden
	
	return False #falls Figur nicht gefunden

def zeichne_rechteck(frame, position, farbe, dicke=2): #Funktion, welche ein Rechteck zeichnet
	x, y, w, h = position
	cv2.rectangle(frame, (x, y), (x+w, y+h), farbe, dicke)

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

def vektor_berechnung(old, new, schwellenwert):
	diff = new-old #Differenz alte und neue Position
	if abs(diff) <= schwellenwert: #unterhalb des Schwellenwertes werden keine Veraenderungen detektiert
		return 0
	if diff < -schwellenwert: #Veränderung Richtung negativ
		return -1
	if diff > schwellenwert: #Veränderung Richtung positiv
		return 1  

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

	ret, frame = cap.read() #Erster Frame wird abgerufen
	y_shape, x_shape, z_shape = frame.shape #Videomaße für den Kopfentwicklungspunkt werden ausgelesen

	global stab #Liste der Taktstockpositionen
	stab = []


	global figuren_anz 
	figuren_anz = 0
	versch_vec = [(0,0),(0,0)] #Liste der vollzogenen Bewegungsvektoren
	koordinaten = [(0,0),(0,0)] # Liste mit Koordinaten der Eckpunkte

	lautstaerke = 0
	while(True):
		ret, frame = cap.read() #Holt Frame



		stab.append(color_rec(frame)) #Ermittelte Taktstockposition wird registriert
		zeichne_kreis(frame,stab[position]) #Kreis wird an aktueller Taktstockposition gezeichnet


		stab_x, stab_y = stab[position-1] #die aktuellen Daten werden aus der Taktstockposition extrahiert

		dynamik_aufruf = 0 # Variable die, 1 ist, wenn eine Ecke erkannt wurde (versch_vec-aenderung), und 0, wenn keine Ecke erkannt wurde
		if position > 1: #ab dieser Position gibt es verwendbare Daten zur Vektorberechnung
			stab_x_old, stab_y_old = stab[position-2] #Letzte Positon

			x_vec = vektor_berechnung(stab_x_old,stab_x,30) #die beiden eindimensionalen Vektoren werden ermittelt (mit der Zeit zweidim)
			y_vec = vektor_berechnung(stab_y_old,stab_y,30)

			vektor = (x_vec,y_vec) #aus diesen wird ein zweidimensionaler gemacht (mit der Zeit dreidim)
			if vektor != versch_vec[-1] and vektor != (0,0): #zur letzten Posiion identische Vektoren und Nullvektoren werden nicht registriert
				versch_vec.append(vektor)
				if figuren_anz >=2:
					ort = (stab_x,stab_y)
					koordinaten.append(ort)
					dynamik_aufruf = 1
							
			frame = cv2.flip(frame,1) #Spiegelung des frames an der Horizonatalen
			if len(versch_vec) > 4: #Die Figuranalyse startet, wenn genügend Vektoren zum Vergleichen abgespeichert sind
				if figur_finden(versch_vec, [(0, -1), (1, 0), (0, 1), (-1, 0)]): #Es wird nach der übergebenen Figur gesucht
					cv2.rectangle(frame,(x_shape-30,y_shape-30),(x_shape-60,y_shape-60),(255,225,0),4) #Falls die Figur gefunden wurde wird ein Rechteck gezeichnet
					figuren_anz = figuren_anz +1
				if figur_finden(versch_vec, [(-1, 0), (0, 1), (1, 0),(0, -1)]): #Hier das Rechteck nochmal in anderer Drehrichtung
					cv2.rectangle(frame,(x_shape-30,y_shape-30),(x_shape-60,y_shape-60),(255,0,225),4)
					figuren_anz = figuren_anz +1
				if figur_finden(versch_vec, [(1,1),(-1,0),(0,-1)]): # rechter Winkel unten rechts, von rechts oben
					cv2.putText(frame, 'Dreieck', (5, y_shape - 5), 1,1, (255,255,0), 1)
				if figur_finden(versch_vec, [(-1,-1),(0,1),(1,0)]): # rechter Winkel unten rechts, von rechts unten
					cv2.putText(frame, 'Dreieck', (5, y_shape - 5), 1,1, (255,0,225), 1)
				if figur_finden(versch_vec, [(1,-1),(-1,0),(0,1)]): # rechter Winkel unten links, von links unten
					cv2.putText(frame, 'Dreieck', (5, y_shape - 5), 1,1, (255,0,225), 1)					
				if figur_finden(versch_vec, [(-1,1),(0,-1),(1,0)]):
					cv2.putText(frame, 'Dreieck', (5, y_shape - 5), 1,1, (255,0,225), 1)		# rechter Winkel unten links, von links oben
				if figur_finden(versch_vec, [(0,1),(0,-1)]):
					cv2.putText(frame, 'Strich', (5, y_shape - 5), 1,1, (255,0,225), 1)									

		
		if position < 120: #Benutzerinstruktionen in den ersten 120 frames
			cv2.putText(frame, 'zum kalibrieren s druecken und zum beenden q.', (5, y_shape - 5), 1,1, (0, 0, 0), 1)
		position +=1 #Framenummer wird um 1 erhöht
		cv2.imshow('frame',frame) #Ergebnis wird angezeigt
		if cv2.waitKey(1) & 0xFF == ord('q'): #'q' zum Beenden drücken
			break
		if cv2.waitKey(1) & 0xFF == ord('s'):  # schwellenwerte festlegen
			schwellenwerte_festlegen(cap)

	cap.release()
	cv2.destroyAllWindows()
	#THE ENDE

if __name__ == "__main__":
	main()
