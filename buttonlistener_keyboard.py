#!/usr/bin/env python3
# coding=UTF-8

from pynput.keyboard import Listener, Key

mpd = None

def init(mpdcontroller):
	print("Init KeyboardListener", mpdcontroller)
	global mpd
	mpd = mpdcontroller
	print("listening for key press")
	with Listener(on_press=onPress, on_release=onRelease) as listener:
		listener.join()

def onPress(key):
	print("Key pressed: {0}".format(key))
	print("mpd:", mpd)
	if key == Key.left:
		mpd.playPrevFile()

	if key == Key.right:
		mpd.playNextFile()

	if key == Key.page_up:
		mpd.playPrevDir()

	if key == Key.page_down:
		mpd.playNextDir()
		
	if key == Key.up:
		mpd.pause()
		
	if key == Key.down:
		mpd.pause()

def onRelease(key):
	print("Key released: {0}".format(key))



