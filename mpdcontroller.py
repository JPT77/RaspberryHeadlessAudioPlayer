#!/usr/bin/env python3
# coding=UTF-8

import sys
import os

sys.path.append(os.path.abspath("/home/jan/Home/Projekte/RaspberryPi/RaspiAudioplayer/PersistentMPDClient"))
# link or copy PersistentMPDClient into local dir
from PersistentMPDClient import PersistentMPDClient

from mpd import MPDClient, MPDError, CommandError

import signal # allow Ctrl-C, never end the program

from speachsyn_python import SpeachSynPython 

# expected file and folder structure
# last dir is book or album name for TTS
# file name is in alphabatical order and contains chapter number for TTS

# clean up on Ctrl-C
def signal_handler(sig, frame):
	print("Received signal:", sig, "-", signal.Signals(sig).name)
	GPIO.cleanup()
	mpd.close()
	mpd.disconnect()
	sys.exit(0)

def get_track_name(track): # for tts
	split1 = track.get("file").split("/")
	split2 = split1[-1].split(".")
	return split1[-2]+ " Kapitel "+split2[0]


class MpdController():
	def __init__(self, mpdserver, tts, gpio, ):
		print ("*** Init MPD")
		mpd = PersistentMPDClient(host=mpdserver, port=6600)
		mpd.timeout = 1                 # network timeout in seconds
		mpd.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None
		print("MPD Version:", mpd.mpd_version)

		self.tts = tts
		self.gpio = gpio

	def init():
		print("*** Init Screen")
		print("Button\t Status\t Queue\t Song")
		printMpdStatus("Init")

		print("*** Init Player")
		printMpdStatus("Init")
		if not mpd.playlistinfo():
			for song in mpd.listall():
				# add first book
				if song.get("directory"):
					print("add dir:", song.get("directory"))
					mpd.add(song.get("directory"))
					break
			printMpdStatus("Added")

		if not mpd.currentsong():
			mpd.play()
			
		speak("Spiele Titel "+ get_track_name(mpd.currentsong()))
		print("*** Init Finished, Button Monitor Online")


	def printMpdStatus(msg):
		print(msg, "\t", mpd.status().get("state"), "\t", len(mpd.playlistinfo()), "\t", mpd.currentsong().get("file"))

	def get_current_book(self, currentsong):
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

	def play_dir(self, richtung, text):
		next_book = get_current_book(mpd.currentsong()) + richtung
		count = -1
		for song in mpd.listall():
			if song.get("directory"):
				count += 1 # count only dir type entries
				if count == next_book:
					mpd.clear()
					mpd.add(song.get("directory"))
					mpd.play()
					print_mpd_status("Book")
					mpd.pause()
					speak("Spiele " + text + " Buch " + get_track_name(mpd.currentsong()))
					mpd.pause()
					return
		printMpdStatus("Book")
		mpd.pause()
		speak("Kein " + text + " Buch vorhanden")
		mpd.pause()

	def playPrevDir(self):
		playDir(-1, "vorheriges")

	def playNextDir(self):
		playDir(+1, "nächstes")

	def playPrevFile(self):
		if not mpd.currentsong() or mpd.status().get("state") == "stop":
			mpd.play()
		mpd.previous()
		printMpdStatus("Left")
		mpd.pause()
		tts.speak("Spiele vorherigen Titel")
		tts.speak(get_track_name(mpd.currentsong()))
		mpd.pause()

	def playNextFile(channel):
		if not mpd.currentsong() or mpd.status().get("state") == "stop":
			mpd.play()
		mpd.next()
		printMpdStatus("Right")
		mpd.pause()
		tts.speak("Spiele nächsten Titel")
		tts.speak(get_track_name(mpd.currentsong()))
		mpd.pause()

	def pause():
		if mpd.status().get("state") == "play":
			mpd.pause()
			tts.speak("Pause")
		else:
			tts.speak("Abspielen")
			mpd.pause()
		printMpdStatus("Play")


tts = SpeachSynPython(150,1.0, "german")
#tts = SpeachSynGoogle("de",False,"cvlc",".")

gpio = None

mpd = MpdController("raspberry", tts, gpio)
#mpd = MpdController("localhost", tts, gpio)

mpd.init()

signal.signal(signal.SIGINT, signal_handler)
signal.pause() # wait for Ctrl-C

