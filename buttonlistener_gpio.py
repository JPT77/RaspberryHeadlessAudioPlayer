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

last_pressed_time = PAST_TIMESTAMP

class GpioListener():
	def __init__(self, playPrevFile, playNextFile, playPrevDir, playNextDir, pause):
		PAST_TIMESTAMP = datetime.datetime(year=2021,month=1,day=1) # a fixed date in the past
		last_pressed_time = PAST_TIMESTAMP

		this.playPrevFile = playPrevFile
		this.playNextFile = playNextFile
		this.playPrevDir  = playPrevDir
		this.playNextDir  = playNextDir
		this.pause = pause

		print ("*** Init GPIO")
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(BTN_LEFT_GPIO,  GPIO.IN)
		GPIO.setup(BTN_PLAY_GPIO,  GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(BTN_RIGHT_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.add_event_detect(BTN_LEFT_GPIO,  GPIO.BOTH, callback=gpioCallback, bouncetime=BTN_DEBOUNCE)
		GPIO.add_event_detect(BTN_PLAY_GPIO,  GPIO.BOTH, callback=gpioCallback, bouncetime=BTN_DEBOUNCE)
		GPIO.add_event_detect(BTN_RIGHT_GPIO, GPIO.BOTH, callback=gpioCallback, bouncetime=BTN_DEBOUNCE)

	def close():
		GPIO.cleanup()

def gpioCallback(button):
	global last_pressed_time

	curr_edge = GPIO.input(button)
	if curr_edge: # button released
		interval = (datetime.datetime.now() - last_pressed_time) / timedelta(milliseconds=1)

		# reset to default to detect missed EDGE FALL
		last_pressed_time = PAST_TIMESTAMP
		#print ("now - pressed", datetime.datetime.now() - cb_pressed_time)
		#print ("interval ms", interval)

		if interval > 60000:
			print ("Error: Interval too long, missed EDGE FALL?", interval)
			return

		if interval <= 500:
			if button == BTN_LEFT_GPIO:
				playPrevFile(button)
			elif button == BTN_RIGHT_GPIO:
				playNextFile(button)
		else:
			if button == BTN_LEFT_GPIO:
				playPrevDir()
			elif button == BTN_RIGHT_GPIO:
				playNextDir()

		else: # button depressed
			cb_pressed_time = datetime.datetime.now()
			if button == BTN_PLAY_GPIO:
				pause(button)

