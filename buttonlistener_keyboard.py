#!/usr/bin/env python3
# coding=UTF-8

from pynput.keyboard import Listener

def init( playPrevFile, playNextFile, playPrevDir, playNextDir, pause):
	this.playPrevFile = playPrevFile
	this.playNextFile = playNextFile
	this.playPrevDir  = playPrevDir
	this.playNextDir  = playNextDir
	this.pause = pause

def onPress(key):
	print("Key pressed: {0}".format(key))
	if key == Key.Left:
		playPrevFile()

	if key == Key.Right:
		playNextFile()

	if key == Key.PageUp:
		playPrevDir()

	if key == Key.PageDown:
		playNextDir()
		
	if key == Key.Up:
		pause()
		
	if key == Key.Down:
		pause()
		
def onRelease(key):
	print("Key released: {0}".format(key))

with Listener(on_press=onPress, on_release=onRelease) as listener:
	listener.join()

