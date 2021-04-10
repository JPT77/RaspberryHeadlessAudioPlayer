#!/usr/bin/env python3
# coding=UTF-8

import sys
import os

#either set the path to PersistentMPDClient/
sys.path.append(os.path.abspath("../PersistentMPDClient"))
# or link or copy PersistentMPDClient.py into local dir, then
from PersistentMPDClient import PersistentMPDClient

from mpd import MPDClient, MPDError, CommandError

import signal # allow Ctrl-C, never end the program

# expected file and folder structure:
# last dir is book or album name for TTS
# file name is in alphabatical order and contains chapter number for TTS

# clean up on Ctrl-C
def signal_handler(sig, frame):
	print("Received signal:", sig, "-", signal.Signals(sig).name)
	GPIO.cleanup()
	mpd.close()
	mpd.disconnect()
	sys.exit(0)

def getTrackName(track): # for tts
	split1 = track.get("file").split("/")
	split2 = split1[-1].split(".")
	return split1[-2]+ " Kapitel "+split2[0]


class MpdController():
	def __init__(self, mpdserver, tts):
		print ("*** Init MPD")
		self.mpd = PersistentMPDClient(host=mpdserver, port=6600)
		self.mpd.timeout = 1                 # network timeout in seconds
		self.mpd.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None
		print("MPD Version:", self.mpd.mpd_version)
		self.tts = tts

	def printMpdStatus(self, msg):
		print(msg, "\t", self.mpd.status().get("state"), "\t", len(self.mpd.playlistinfo()), "\t", self.mpd.currentsong().get("file"))

	def init(self):
		print("*** Init Screen")
		print("Button\t Status\t Queue\t Song")
		self.printMpdStatus("Init")

		print("*** Init Player")
		self.printMpdStatus("Init")
		if not self.mpd.playlistinfo():
			for song in self.mpd.listall():
				# add first book
				if song.get("directory"):
					print("add dir:", song.get("directory"))
					self.mpd.add(song.get("directory"))
					break
			self.printMpdStatus("Added")

		if not self.mpd.currentsong():
			self.mpd.play()
			
#		tts.speak("Spiele Titel "+ getTrackName(self.mpd.currentsong()))
		print("*** Init Finished, Button Monitor Online")

	def getCurrentBook(self, currentsong):
		count = -1
		split = currentsong.get("file").split("/")
		bookname = split[-2]
		for song in self.mpd.listall():
			dir = song.get("directory")
			if dir:
				count += 1 # count only dir type entries
				if dir == bookname:
					return count
		return -1

	def playDir(self, richtung, text):
		next_book = self.getCurrentBook(self.mpd.currentsong()) + richtung
		count = -1
		for song in self.mpd.listall():
			if song.get("directory"):
				count += 1 # count only dir type entries
				if count == next_book:
					self.mpd.clear()
					self.mpd.add(song.get("directory"))
					self.mpd.play()
					self.printMpdStatus("Book")
					self.mpd.pause()
					tts.speak("Spiele " + text + " Buch " + getTrackName(self.mpd.currentsong()))
					self.mpd.pause()
					return
		self.printMpdStatus("Book")
		self.mpd.pause()
		tts.speak("Kein " + text + " Buch vorhanden")
		self.mpd.pause()

	def playPrevDir(self):
		self.playDir(-1, "vorheriges")

	def playNextDir(self):
		self.playDir(+1, "nächstes")

	def playPrevFile(self):
		if not self.mpd.currentsong() or self.mpd.status().get("state") == "stop":
			self.mpd.play()
		self.mpd.previous()
		self.printMpdStatus("Left")
		self.mpd.pause()
		tts.speak("Spiele vorherigen Titel")
		tts.speak(getTrackName(self.mpd.currentsong()))
		self.mpd.pause()

	def playNextFile(self):
		if not self.mpd.currentsong() or self.mpd.status().get("state") == "stop":
			self.mpd.play()
		self.mpd.next()
		self.printMpdStatus("Right")
		self.mpd.pause()
		tts.speak("Spiele nächsten Titel")
		tts.speak(getTrackName(self.mpd.currentsong()))
		self.mpd.pause()

	def pause(self):
		if self.mpd.status().get("state") == "play":
			self.mpd.pause()
			tts.speak("Pause")
		else:
			tts.speak("Abspielen")
			self.mpd.pause()
		self.printMpdStatus("Play")

print ('Number of arguments:', len(sys.argv), 'arguments.')
print ('Argument List:', str(sys.argv))

if len(sys.argv) != 4:
	print("Usage:", sys.argv[0], "<Server> <SpeachSyn> <ButtonMonitor>")
	print("\t Server: localhost, servername or IP address")
	print("\t Speachsynthesizer: System or Google")
	print("\t Buttonmonitor: Keyboard or GPIO")
	sys.exit(-1)

syn = sys.argv[2].upper()
if syn == "SYSTEM":
	from speachsyn_python import SpeachSynPython
	tts = SpeachSynPython(150,1.0, "german")
elif syn == "GOOGLE":
	from speachsyn_google import SpeachSynGoogle
	tts = SpeachSynGoogle("de",False,"cvlc",".")
else:
	print("Unknown Synth:", syn, "Using default SpeachSynthesizer System")
	from speachsyn_python import SpeachSynPython
	tts = SpeachSynPython(150,1.0, "german")

mpc = MpdController(mpdserver=sys.argv[1], tts=tts)

mpc.init()

buttons = sys.argv[3].upper()
if buttons == "KEYBOARD":
	import buttonlistener_keyboard
	buttonlistener_keyboard.init(mpc)
elif buttons == "GPIO":
	import buttonlistener_gpio
	buttonlistener_gpio.init(mpc)
else:
	print("Unknown ButtonMonitor:", buttons, "Using default GPIO")
	import buttonlistener_gpio
	buttonlistener_gpio.init(mpc)

#signal.signal(signal.SIGINT, signal_handler)
#signal.pause() # wait for Ctrl-C

