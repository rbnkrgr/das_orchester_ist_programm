#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Musik_abspielen.py
#  
#  Copyright 2016 Stefan Born <born@math.tu-berlin.de>
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

import midi
import time 
import fluidsynth
import threading




def test1():
	fs = fluidsynth.Synth() 
	fs.start(driver="alsa")

	sfid = fs.sfload("FluidR3_GM.sf2") 
	fs.program_select(0, sfid, 0, 0)

	fs.noteon(0, 60, 50) 
	fs.noteon(0, 67, 30) 
	fs.noteon(0, 76, 30)

	time.sleep(1.0)

	fs.noteoff(0, 60) 
	fs.noteoff(0, 67) 
	fs.noteoff(0, 76)

	time.sleep(1.0)

	fs.delete() 


class Player(object):
	
	def __init__(self):
		self.d=[]
		self.fs = fluidsynth.Synth() 
		self.fs.start(driver="alsa")

		self.sfid = self.fs.sfload("FluidR3_GM.sf2") 
		self.fs.program_select(0, self.sfid, 0, 0)
		
		self.tick_duration = 0.002
		
	def load(self, filename):
		'''lädt ein Midi-File mit Namen filename.'''
		with open(filename,'rb') as f:
			self.d=midi.fileio.read_midifile(f)
		self.d.make_ticks_abs()
		
	def play(self):
		'''spielt die Datei in Echtzeit ab, die zugrundeliegende
		Zeiteinheit self.tick_duration lässt sich während des Abspielens
		ändern.'''
		
		for voice in self.d:
			voice_thread = threading.Thread(target=self.play_voice, args=(voice,))
			voice_thread.start()
		
	def play_voice(self,voice):
		voice.sort(key=lambda e: -e.tick)

		tick_now = 0
	
		time_now = time.time()
		
		while len(voice)>0:
			event=voice.pop()
			while event.tick>tick_now:
				#print event
				time.sleep(self.tick_duration-time.time()+time_now)
				tick_now +=1 
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
		
	
if __name__ == "__main__":
	import numpy as np
	p=Player()
	p.load('symphony_6_1_(c)lucarelli.mid')
	p.tick_duration=0.004
	p.play()
