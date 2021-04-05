#!/usr/bin/python3
# coding: utf-8

import dbus
import sys
import threading, time
import dbus

from gi.repository import Gio

MOUNT_DIR = "/var/lib/mpd/music/usb"

class Automount():
	def __init__(self, device, target):
		self.device = device
		self.target = target

	def Mount(self):
		print("mount: ")
	
	def UnMount(self):
		print("unmount: ")
	
	def TriggerLibScan(self):
		print("TriggerLibScan: ")

def callback_function(*args):
	print('Received something .. ', args)
	
def start_listening():
	import dbus
	from dbus.mainloop.glib import DBusGMainLoop
	DBusGMainLoop(set_as_default=True)

	bus = dbus.SystemBus()

	def cb_insert_disk(*args):
		device = args[0]
		info = args[1]
		print("***** ADDED", device)
		if "org.freedesktop.UDisks2.Block" in info:
#			print("Added Disk 1B: ", info['org.freedesktop.UDisks2.Block'])
			if 'org.freedesktop.UDisks2.Partition' in info:
				drive = info['org.freedesktop.UDisks2.Block']['Drive']
				fs = info['org.freedesktop.UDisks2.Partition']['Type']
				#print("Added Disk 1P:", args[1]['org.freedesktop.UDisks2.Partition'])
				print("Mounting", fs, device, "on", drive, "to ...")
				
				obj = bus.get_object('org.freedesktop.UDisks2', device)
				#obj.Mount(dict(fstype=fs, options="ro"), dbus_interface="org.freedesktop.UDisks2.Filesystem")
				mountpoint = obj.Mount(dict(options="ro"), dbus_interface="org.freedesktop.UDisks2.Filesystem")
				print("Mounted to ", mountpoint)
				
			else : 
				print(device, "is not a partition. Skipping.")
		else : 
			print(device,"is not a block device. Skipping.")

	def cb_remove_disk(*args):
		device = args[0]
		info = args[1]
		print("***** REMOVED ", device)
		if "org.freedesktop.UDisks2.Block" in info:
			if 'org.freedesktop.UDisks2.Partition' in info:
				print("Unmounting", device)
#				obj = bus.get_object('org.freedesktop.UDisks2', device)
#				obj.Unmount(dbus_interface="org.freedesktop.UDisks2.Filesystem")
			else : 
				print(device, "is not a partition. Skipping.")
		else : 
			print(device, "is not a block device. Skipping.")

	bus.add_signal_receiver(cb_insert_disk, 'InterfacesAdded',   'org.freedesktop.DBus.ObjectManager')
	bus.add_signal_receiver(cb_remove_disk, 'InterfacesRemoved', 'org.freedesktop.DBus.ObjectManager')

	# Let's start the loop
	from gi.repository import GObject
	loop = GObject.MainLoop()
	loop.run()


#am = Automount("test", "test")
#print(am.GetDevices())

# Our thread will run start_listening
thread=threading.Thread(target=start_listening)
thread.daemon=True # This makes sure that CTRL+C works
thread.start()

# And our program will continue in this pointless loop
while True:
    time.sleep(1)

