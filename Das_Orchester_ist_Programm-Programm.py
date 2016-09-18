#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Das_Orchester_ist_Programm-Programm.py
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
import time
import random
import numpy as np
import cv2
import sys
from copy import deepcopy
import pickle
import midi
import fluidsynth
import threading
import os

#=====Object from Stefan=====#

class Player(object):
	
	def __init__(self):
		self.d=[]
		self.fs = fluidsynth.Synth() 
		self.fs.start(driver="alsa")

		self.sfid = self.fs.sfload("FluidR3_GM.sf2") 
		self.fs.program_select(0, self.sfid, 0, 0)
		
		self.tick_duration = 0.01
		
		
	def load(self, filename):
		'''lädt ein Midi-File mit Namen filename.'''
		with open(filename,'rb') as f:
			self.d=midi.fileio.read_midifile(f)
		self.d.make_ticks_abs()
		
	def play(self):
		'''spielt die Datei in Echtzeit ab, die zugrundeliegende
		Zeiteinheit self.tick_duration lässt sich während des Abspielens
		ändern.'''
		self.stop = False
		for voice in self.d:
			voice_thread = threading.Thread(target=self.play_voice, args=(voice,))
			voice_thread.start()
		
	def stopit(self):
		self.stop = True
		
	def play_voice(self,voice):
		voice.sort(key=lambda e: -e.tick)

		tick_now = 0
	
		time_now = time.time()
		
		while len(voice)>0 and not self.stop :
			event=voice.pop()
			while event.tick>tick_now:
				#print event
				n_ticks= max(int((time.time()-time_now)//self.tick_duration)+1,event.tick-tick_now)
				#print n_ticks, n_ticks*self.tick_duration-time.time()+time_now
				time.sleep(n_ticks*self.tick_duration-time.time()+time_now)
				tick_now +=n_ticks
				time_now=time.time()
			
			self.send(event)	
			
	def send(self, event):
		'''Diese Methode kommuniziert mit dem Synthesizer. Bisher sind
		nur drei Ereignistypen implementiert.'''
		if type(event) is midi.NoteOnEvent:
			self.fs.noteon(event.channel,event.data[0],event.data[1])
		elif type(event) is midi.NoteOffEvent:
			self.fs.noteoff(event.channel, event.data[0])
		elif type(event) is midi.ProgramChangeEvent:
			self.fs.program_change(event.channel, event.data[0])
		elif type(event) is midi.ControlChangeEvent:
			self.fs.cc(event.channel, event.data[0],event.data[1])
			
#=====Functions=====#

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

def detect_gesture(zu_untersuchen, figur):
	figurlaenge = len(figur)
	
	zu_untersuchen_kurz = [] #Diese Liste soll die letzten dirigierten Vektoren enthalten, die wichtig sind
	for i in range(figurlaenge,0,-1):	#von index -1 bis index 0
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
	
def detect_bpm(l):
	global a
	global b
	global bpm
	if l > 2:
		b = time.clock()
		bpm = 60/(b-a)
		a = b
	else:
		a = time.clock()

def get_vec(old, new):
	if new == None:
		return None
	elif old == new:
		return None
	elif old == 1:
		if new == 2:
			return (1,0)
		elif new == 3:
			return (1,-1)
		elif new == 4:
			return (0,-1)
	elif old == 2:
		if new == 1:
			return (-1,0)
		elif new == 3:
			return  (0,-1)
		elif new == 4:
			return (-1,-1)
	elif old == 3:
		if new == 1:
			return (-1,1)
		elif new == 2:
			return (0,1)
		elif new == 4: 
			return (-1,0)
	elif old == 4:
		if new == 1:
			return (0,1)
		elif new == 2:
			return (1,1)
		elif new == 3:
			return (1,0)

def get_visual(pos):
	if new == 1:
		cv2.circle(frame, c1, cthresh, color, 3)
		cv2.circle(clean, c1, cthresh, color, 3)
	if new == 2:
		cv2.circle(frame, c2, cthresh, color, 3)
		cv2.circle(clean, c2, cthresh, color, 3)
	if new == 3:
		cv2.circle(frame, c3, cthresh, color, 3)
		cv2.circle(clean, c3, cthresh, color, 3)
	if new == 4:
		cv2.circle(frame, c4, cthresh, color, 3)
		cv2.circle(clean, c4, cthresh, color, 3)
		
	cv2.circle(frame, c1, cthresh, color, 3)
	cv2.circle(frame, c2, cthresh, color, 3)
	cv2.circle(frame, c3, cthresh, color, 3)
	cv2.circle(frame, c4, cthresh, color, 3)
	cv2.circle(frame, pos, 4, (0,0,255), -1)	
	cv2.circle(clean, pos, 4, (0,0,255), -1)
	cv2.circle(frame, (640,480), cthresh, (0,255,255), -1)	
	
def get_length(a,b):			#berechnet länge eines vektors von 2 punkten
	ax, ay = a
	bx, by = b
	cx = ax - bx
	cy = ay - by
	l = np.sqrt(cx**2+cy**2)
	return l
	
def in_circle(pos):
	
	vec1 = get_length(c1, pos)		#sammlung der längen der vektoren von den mittelpunkten zur position
	vec2 = get_length(c2, pos)
	vec3 = get_length(c3, pos)
	vec4 = get_length(c4, pos)
	vecmenu = get_length(cmenu, pos)
	
	lengths = [cthresh+1, vec1, vec2, vec3, vec4, vecmenu]
	
	for x in lengths:
		if x < cthresh:
			ret = lengths.index(x)
			if ret == 5:
				return "menu"
			return ret
		
def detect_gesture(zu_untersuchen, figur): #diese Funktion versucht Figuren im Dirigat zu erkennen. Dafuer bekommt sie die Figurvektoren in richtiger Reihenfolge, sowie die Liste mit den dirigierten Vektoren uebergeben
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

def beat_number(vec,figure):
	a,b = vec
	
	if figure == 'triangleA':
		if vec == (0,-1):
			return 1
		if vec == (-1,0):
			return 2 
		else:
			return 3
	if figure == 'triangleB':
		if vec == (1,0):
			return 1
		if vec == (0,1):
			return 2 
		else:
			return 3
	if figure == 'triangleC':
		if vec == (-1,0):
			return 1
		if vec == (0,1):
			return 2 
		else:
			return 3
	if figure == 'triangleD':
		if vec == (0,-1):
			return 1
		if vec == (1,0):
			return 2 
		else:
			return 3

	if figure == 'rectangleCCW':
		if vec == (0,-1):
			return 1
		if vec == (1,0):
			return 2
		if vec == (0,1):
			return 3
		if vec == (-1,0):
			return 4
	if figure == 'rectangleCW':
		if vec == (0,-1):
			return 4
		if vec == (1,0):
			return 3
		if vec == (0,1):
			return 2
		if vec == (-1,0):
			return 1

	if figure == 'line':
		if vec == (0,-1):
			return 1
		else:
			return 2
	else:
		return False	
		
def check_gestures():
	global figure
	if len(veclist) > 4:
		if detect_gesture(veclist, rectangleCW):
				figure = "rectangleCW"
				counter()
		if detect_gesture(veclist, rectangleCCW):
				figure = "rectangleCCW"
				counter()
		if detect_gesture(veclist, triangleA):
				figure = "triangleA"
				counter()
		if detect_gesture(veclist, triangleB):
				figure = "triangleB"
				counter()
		if detect_gesture(veclist, triangleC):
				figure = "triangleC"
				counter()
		if detect_gesture(veclist, triangleD):
				figure = "triangleD"
				counter()
		if detect_gesture(veclist, line):
				figure = "line"
				counter()
		
def counter():
	f = len(figure)
	if f > 10:
		r = 4 
	else:
		r = int(np.sqrt(f))
		
	cv2.putText(mirror, str(beat_number(veclist[-1],figure)) + "/" + str(r), (40,40), 2, 1, (255,255,255), 0)
	return r

def bpm_mean(bpm):
	if bpm > 40:
		bpmlist.append(bpm)
		if len(bpmlist) < 10:
			npbpm = np.array(bpmlist)
			mean = int(np.mean(npbpm))/10
			mean = int(mean)*20
			
		else:
			rel = bpmlist[-10:]
			npbpm = np.array(rel)
			mean = int(np.mean(npbpm))/10
			mean = int(mean)*10
		return mean
	return bpm
		
def tick_laenge_ermitteln(bpm):
	if (60/ bpm)/192 > 0:				#1 tick 0,1s# 1 viertel 19,2s#
		l=(60/ bpm)/192
		return l
		
def menu_visual(cap):
	while(True): 
		_, frame = cap.read()
		position = detect_color(frame)
		
		new = in_circle(position)

		if new != "menu":
			break
			
		frame = cv2.flip(frame,1) 
		
		#===Menü===#
		cv2.circle(frame, (0,480), cthresh, (0,255,255), -1)	
		cv2.putText(frame, "INFO", (200,80), 2, 1, (255,255,255), 0)
		cv2.putText(frame, "Kalibrieren [K]", (200,130), 2, 1, (255,255,255), 0)
		cv2.putText(frame, "Beenden [Leer]", (200,170  ), 2, 1, (255,255,255), 0)
		#===Ende===#
		
		cv2.imshow('frame', frame)
		
		if cv2.waitKey(1) & 0xFF == ord(' '): 
			cap.release()
			sys.exit()
		
def waehle_stueck(taktart, lager_verzeichnis):
	if taktart == 4:
		stuecke = os.listdir(lager_verzeichnis + "/4_4")
		art = "4_4"
	elif taktart == 2:	
		stuecke = os.listdir(lager_verzeichnis + "/2_2")
		art = "2_2"
	elif taktart == 3:
		stuecke = os.listdir(lager_verzeichnis + "/3_4")
		art = "3_4"
	else:
		print "Ungueltige Taktart"
	auswahl = random.choice(stuecke)
	return  lager_verzeichnis +  "/" + art + "/" + auswahl

#=======gestures=======#

rectangleCW = [(1,0),(0,-1),(-1,0),(0,1)]
rectangleCCW = [(1,0),(0,1),(-1,0),(0,-1)]  
triangleA = [(1,1),(0,-1),(-1,0)]
triangleB = [(-1,-1),(1,0),(0,1)]
triangleC = [(1,-1),(-1,0),(0,1)]
triangleD = [(-1,1),(0,-1),(1,0)]
line = [(0,1),(0,-1)]
gestures = [rectangleCW, rectangleCCW, triangleA, triangleB, triangleC, triangleD, line]

#=======circles=======#

c1 = ((320+120),(240-120))
c3 = ((320-120),(240+120))
c2 = ((320-120),(240-120))
c4 = ((320+120),(240+120))
cmenu = (640,480)
color = (10,10,255)

#=======variables=======#

global fnr, bpm, new

fnr = 0							
bpm = 0
cthresh = 95			
ref = (320,240)
old = 0	
new = 5

#=======lists=======#

veclist = [None]						#liste beinhaltet richtungsänderungen
bpmlist = []

#=======program=======#

cap = cv2.VideoCapture(0)
schwellenwerte_einlesen()

while True:
	_, frame = cap.read()	
	clean = np.copy(frame)

	position = detect_color(frame)
	
	get_visual(position)
	
	new = in_circle(position)

	if new == "menu":
		menu_visual(cap)
		continue
	
	vec = get_vec(old, new)
	
	if vec != None and vec != veclist[-1]:
		veclist.append(vec)
		detect_bpm(len(veclist))
		
	if new != None and new != old:
		old = new
	
	bpm = bpm_mean(bpm)
		
	frame = cv2.addWeighted(frame, 0.5, clean, 0.5, 0)
	mirror = cv2.flip(frame,1)
	
	check_gestures()
				
	cv2.putText(mirror, str(int(bpm)), (560,40), 2, 1, (255,255,255), 0)
	
	cv2.imshow("frame", mirror)
	fnr += 1

	if fnr == 200:
		try:
			p = Player()
			p.load(waehle_stueck(counter(), "../Midi"))
			p.play()
		except:
			print "Bitte neu starten und Dirigieren."
	if fnr > 200:
		try:
			if bpm > 0:
				p.tick_duration = tick_laenge_ermitteln(bpm)
		except:
			print "Fehler. Bitte neu starten."
		
	if cv2.waitKey(1) & 0xFF == ord('k'):
		get_values(cap)

	if cv2.waitKey(1) & 0xFF == ord(' '):
		if fnr > 200:
			p.stopit()
		print "herunterfahren"
		break	

cap.release()
cv2.destroyAllWindows()

