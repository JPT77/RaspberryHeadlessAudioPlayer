#!/usr/bin/env python3
# coding=UTF-8

import sys
import RPi.GPIO as GPIO

import datetime # button debounce
from datetime import timedelta

BTN_LEFT_GPIO = 3
BTN_PLAY_GPIO = 15
BTN_RIGHT_GPIO = 27

BTN_DEBOUNCE = 50

# just a random fixed date in the past for last_pressed_time initialization
PAST_TIMESTAMP = datetime.datetime(year=2021,month=1,day=1)
last_pressed_time = PAST_TIMESTAMP

mpd = None

def init(mpdcontroller):
	global mpd
	mpd = mpdcontroller

	print ("*** Init GPIO")
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(BTN_LEFT_GPIO,  GPIO.IN)
	GPIO.setup(BTN_PLAY_GPIO,  GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(BTN_RIGHT_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.add_event_detect(BTN_LEFT_GPIO,  GPIO.BOTH, callback=onGpio, bouncetime=BTN_DEBOUNCE)
	GPIO.add_event_detect(BTN_PLAY_GPIO,  GPIO.BOTH, callback=onGpio, bouncetime=BTN_DEBOUNCE)
	GPIO.add_event_detect(BTN_RIGHT_GPIO, GPIO.BOTH, callback=onGpio, bouncetime=BTN_DEBOUNCE)

def onGpio(button):
	global last_pressed_time

	curr_edge = GPIO.input(button)
	if curr_edge: # button released,
		# for left and right buttons we do action on button release
		# because long press is next dir/album/book, short press is next track

		# time since last button down in ms
		interval = (datetime.datetime.now() - last_pressed_time) / timedelta(milliseconds=1)

		# reset to default to detect missed EDGE FALL
		last_pressed_time = PAST_TIMESTAMP
		#print ("time now() minus last pressed", datetime.datetime.now() - last_pressed_time)
		#print ("equals interval mseconds", interval)

		if interval > 60000: # nobody presses the button for 60 sec, timing issue or bug
			print ("Error: Button pressed too long, missed edge fall/button press?", interval)
			return

		if interval <= 500: # file operation
			if button == BTN_LEFT_GPIO:
				mpd.playPrevFile()
			elif button == BTN_RIGHT_GPIO:
				mpd.playNextFile()
			# BTN_PLAY ignored
		else: # interval > 500 ms -> dir operation
			if button == BTN_LEFT_GPIO:
				mpd.playPrevDir()
			elif button == BTN_RIGHT_GPIO:
				mpd.playNextDir()
			# BTN_PLAY ignored

	else: # button depressed
		last_pressed_time = datetime.datetime.now()
		if button == BTN_PLAY_GPIO:
			mpd.pause()

