#!/usr/bin/python3
# coding: utf-8

import dbus
import sys
import threading, time
import dbus

from gi.repository import Gio

def startAutomounter():
	import dbus
	from dbus.mainloop.glib import DBusGMainLoop
	DBusGMainLoop(set_as_default=True)
	bus = dbus.SystemBus()

	def onInsertDisk(*args):
		device = args[0]
		info = args[1]
#		print("***** ADDED", device)
		if "org.freedesktop.UDisks2.Block" in info:
			if 'org.freedesktop.UDisks2.Partition' in info:
				drive = info['org.freedesktop.UDisks2.Block']['Drive']
				print("Mounting", device, "on", drive)
				obj = bus.get_object('org.freedesktop.UDisks2', device)
				mountpoint = obj.Mount(dict(options="ro"), dbus_interface="org.freedesktop.UDisks2.Filesystem")
				print("Mounted to ", mountpoint)

	bus.add_signal_receiver(onInsertDisk, 'InterfacesAdded',   'org.freedesktop.DBus.ObjectManager')

	# start the listener loop
	from gi.repository import GLib
	loop = GLib.MainLoop()
	loop.run()

def init(mpdcontroller):
	# start the listener thread
	thread=threading.Thread(target=startAutomounter)
	thread.daemon=True # enable Ctrl+C
	thread.start()

# run program in an endless loop until Ctrl-C
#import time
#while True:
#	time.sleep(1)

