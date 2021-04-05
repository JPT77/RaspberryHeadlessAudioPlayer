#!/usr/bin/python3
# coding: utf-8

import pyttsx3

class SpeachSynPython():
	def __init__(self, rate, volume, language):
		print ("*** Init Python Text-To-Speech")
		self.tts = pyttsx3.init()
		self.tts.setProperty('rate',   rate)
		self.tts.setProperty('volume', volume)
		self.tts.setProperty("voice",  language)

	def speak(self, text):
		print("Speaking:", text)
		self.tts.say(text)
		self.tts.runAndWait()


tts = SpeachSynPython(150, 1.0, "german")
tts.speak("Hallo")
