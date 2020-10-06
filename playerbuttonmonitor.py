#!/usr/bin/env python3
# coding=UTF-8

from mpd import MPDClient, MPDError, CommandError

import pyttsx3

import signal # allow Ctrl-C, never end the program
import sys
import RPi.GPIO as GPIO

BTN_LEFT_GPIO = 3
BTN_PLAY_GPIO = 15
BTN_RIGHT_GPIO = 27

BTN_DEBOUNCE = 300

# clean up on Ctrl-C
def signal_handler(sig, frame):
  print("Received signal:", sig, "-", signal.Signals(sig).name)
  GPIO.cleanup()
  mpd.close()                     # send the close command
  mpd.disconnect()                # disconnect from the server
  sys.exit(0)

#    try:
#      mpd.next()
#    except MPDError as e:
#      if isinstance(e, CommandError):
#        speak("Es wird gerade kein Titel gespielt")
#      else:
#        print(type(e))
#        print(e)
#        speak ("Fehler: ")

def get_track_name(track):
  split1 = track.get("file").split("/")
  split2 = split1[-1].split(".")
  return split1[-2]+ " Kapitel "+split2[0]

def btn_left_cb(channel):
  if not mpd.currentsong() or mpd.status().get("state") == "stop":
    mpd.play()
  mpd.previous()
  mpd.pause()
  speak("Spiele vorherigen Titel "+ get_track_name(mpd.currentsong()))
  mpd.pause()
  print_mpd_status("Left")

def btn_play_cb(channel):
  if mpd.status().get("state") == "play":
    mpd.pause()
    speak("Pausihrt")
  else:
    speak("Abspielen")
    mpd.pause()
  print_mpd_status("Play")

def btn_right_cb(channel):
  if not mpd.currentsong() or mpd.status().get("state") == "stop":
    mpd.play()
  mpd.next()
  mpd.pause()
  speak("Spiele nächsten Titel "+ get_track_name(mpd.currentsong()))
  mpd.pause()
  print_mpd_status("Right")

def print_mpd_status(msg):
  print(msg, "\t", mpd.status().get("state"), "\t", len(mpd.playlistinfo()), "\t", mpd.currentsong().get("file"))

def speak(msg):
  print("Speaking:", msg)
  tts.say(msg)
  tts.runAndWait()

if __name__ == '__main__':

  print ("*** Init Text-To-Speech")
  tts  = pyttsx3.init()
  tts.setProperty('rate', 150)
  tts.setProperty('volume', 1.0)
  tts.setProperty("voice", "german")

  print ("*** Init GPIO")
  GPIO.setmode(GPIO.BCM)

  GPIO.setup(BTN_LEFT_GPIO,  GPIO.IN)
  GPIO.setup(BTN_PLAY_GPIO,  GPIO.IN, pull_up_down=GPIO.PUD_UP)
  GPIO.setup(BTN_RIGHT_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#    GPIO.add_event_detect(BUTTON_GPIO, GPIO.FALLING, callback=button_pressed_callback, bouncetime=100)

  GPIO.add_event_detect(BTN_LEFT_GPIO,  GPIO.FALLING, callback=btn_left_cb,  bouncetime=BTN_DEBOUNCE)
  GPIO.add_event_detect(BTN_PLAY_GPIO,  GPIO.FALLING, callback=btn_play_cb,  bouncetime=BTN_DEBOUNCE)
  GPIO.add_event_detect(BTN_RIGHT_GPIO, GPIO.FALLING, callback=btn_right_cb, bouncetime=BTN_DEBOUNCE)

  print ("*** Init MPD")
  mpd = MPDClient()
  mpd.timeout = 1                 # network timeout in seconds
  mpd.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None
  mpd.connect("localhost", 6600)
  print("MPD Version:", mpd.mpd_version)

  print("*** Init Screen")
  print("Button\t Status\t Queue\t Song")
  print_mpd_status("Init")

  print("*** Init Player")
  if not mpd.playlistinfo():

    for song in mpd.listall():
       # füge alle Titel hinzu, hoffentlich alphabetisch
#      if song.get("file"):
#        print("add song:", song.get("file"))
#        mpd.add(song.get("file"))

      # füge erstes Verzeichnis hinzu
      if song.get("directory"):
        print("add dir:", song.get("directory"))
        mpd.add(song.get("directory"))
        break
    print_mpd_status("Added")

  if not mpd.currentsong():
    speak("Spiele Titel "+ get_track_name(mpd.currentsong()))
    mpd.play()

  signal.signal(signal.SIGINT, signal_handler)
  signal.pause() # wait for Ctrl-C
