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
#			print("Added Disk 1B: ", info['org.freedesktop.UDisks2.Block'])
			if 'org.freedesktop.UDisks2.Partition' in info:
				drive = info['org.freedesktop.UDisks2.Block']['Drive']
				#fs = info['org.freedesktop.UDisks2.Partition']['Type']
				#print("Added Disk 1P:", args[1]['org.freedesktop.UDisks2.Partition'])
				print("Mounting", device, "on", drive)

				obj = bus.get_object('org.freedesktop.UDisks2', device)
				#obj.Mount(dict(fstype=fs, options="ro"), dbus_interface="org.freedesktop.UDisks2.Filesystem")
				mountpoint = obj.Mount(dict(options="ro"), dbus_interface="org.freedesktop.UDisks2.Filesystem")
				print("Mounted to ", mountpoint)

	def onRemoveDisk(*args):
		device = args[0]
		info = args[1]
		print("***** REMOVED ", device)
		if "org.freedesktop.UDisks2.Block" in info:
			if 'org.freedesktop.UDisks2.Partition' in info:
				print("Unmounting", device)
#				obj = bus.get_object('org.freedesktop.UDisks2', device)
#				obj.Unmount(dbus_interface="org.freedesktop.UDisks2.Filesystem")

	bus.add_signal_receiver(onInsertDisk, 'InterfacesAdded',   'org.freedesktop.DBus.ObjectManager')
	#bus.add_signal_receiver(onRemoveDisk, 'InterfacesRemoved', 'org.freedesktop.DBus.ObjectManager')

	# start the listener loop
	from gi.repository import GLib
	loop = GLib.MainLoop()
	loop.run()

# start the listener thread
thread=threading.Thread(target=startAutomounter)
thread.daemon=True # enable Ctrl+C 
thread.start()

# run program in an endless loop until Ctrl-C
while True:
    time.sleep(1)

