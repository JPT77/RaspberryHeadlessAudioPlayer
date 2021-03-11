#!/bin/bash

function must_install(){ 
	return "$(apt -qq list $var --installed 2> /dev/null |wc -l)"  # not for scripts
#	[ $(dpkg -s $var >/dev/null 2>&1) ] # wrong result when not purged
}

function pause() {
	echo $@
	read foo
}

function message() {
	echo \#\#\# $@
}

function work() {
	echo DEBUG $@
}

function install_if() { 
	unset install
	for var in "$@"
	do
		if $(must_install $var)
		then
			install+="${var} "
#			echo -n I # install
# 		else
#			echo -n S # skip
		fi
	done
	if [ -n "$install" ];
	then 
#		echo
		work sudo apt-get install -qy $install
	fi
}

# exit on error
set -e

echo This script installs a systemd service and several debian and python packages. 
echo It is going to ask for root password if you didn\'t execute it with root privileges already.
echo
pause Press Enter to continue or Ctrl-C to abort.

if [ $(systemctl is-active --quiet sshd) ];
then
	message SSH Server already running, skipped.
else 
	message Install SSH Server 
	install_if openssh-server
	message Enable SSH Server 
	work sudo systemctl enable ssh
	work sudo systemctl start ssh
fi

message Install Wifi requirements
install_if network-manager-gnome

message If you want to login from network to continue the install script, 
message press Ctrl-C now, set up Wifi if needed 
message then do your remote login and restart the script.
pause Press Enter to continue...

#/etc/hostname setzen, anschliessend Reboot?

#NTP einrichten, um die Uhrzeit automatisch einzustellen

#/etc/systemd/timesyncd.conf

message System update. This may take an hour or more.
work sudo apt-get -q update
work sudo apt-get -qy upgrade

echo \#\#\# Install Media Player Daemon and Command Line Client
install_if mpd mpc

echo \#\#\# Install Libraries
install_if git libespeak1 python3-pip
#sudo apt-get -q install git libespeak1 python3-pip 

# TODO Pakete für manuelle Audiosteuerung???

# optional command line tools for GPIO
install_if gpio-utils

# next may be installed via pip3 instead, if libraries are too old.
install_if python3-mpd python3-gst-1.0 python3-rpi.gpio
#pip3 install python3-mpd? python3-gst-1.0? python3-rpi.gpio? ???

# must be installed via pip3, no apt-get -q package available
work pip3 install pyttsx3

echo \#\#\# Install our player script as daemon
work sudo cp playerbuttonmonitor.service /etc/sytemd/system
work sudo chmod 644 		/etc/sytemd/system/playerbuttonmonitor.service
work sudo chown root:root 	/etc/sytemd/system/playerbuttonmonitor.service
work sudo systemctl enable 	playerbuttonmonitor.service
work sudo systemctl start 	playerbuttonmonitor.service



