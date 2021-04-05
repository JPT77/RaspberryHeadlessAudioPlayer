#!/usr/bin/python3
# coding: utf-8

import os
from gtts import gTTS

def deleteOldMp3(path, pattern): 
	import os
	import glob
	fileList = glob.glob(path + "/" + pattern)
	for filePath in fileList:
		try:
			os.remove(filePath)
		except:
			print("Error while deleting file : ", filePath)

class SpeachSynGoogle():
	def __init__(self, language, slow, player, tempdir):
		self.language = language
		self.slow = slow
		self.player = player
		self.tempdir = tempdir
		deleteOldMp3(tempdir, "*.mp3")

	def speak(self, text):
		print("text: ", text)
		key = hash(text) & (2**64-1)
		filename = tempdir+"/{0:x}.mp3".format(key)
		if os.path.isfile(filename):
			print(filename, "found file, playing")
		else: 
			print(filename, "does not exist yet, render")
			audio_created = gTTS(text=text, lang=self.language, slow=self.slow)
			audio_created.save(filename)
		os.system(f'{self.player} {filename}')


tts = SpeachSynGoogle("en", False, "cvlc", ".")
tts.speak("The fox jumps over the lazy dog")
tts.speak("The fox jumps over the lazy dog")


