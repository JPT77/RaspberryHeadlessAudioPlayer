#!/bin/sh

is_installed(){ 
	# a package having config files still installed will show as installed. Purge first.
	[ ! dpkg -s $pkgs >/dev/null 2>&1 ]
}

install_if(){ 
	$install = ""
	for var in "$@"
	do
		if [ ! is_installed($var) ];
		then
			$install+="${var} "
			echo -n .
		fi
	done
	if [ -n "$install" ];
		sudo apt-get install -qy $install
		echo
	fi
}

echo This script installs a systemd service and several debian and python packages. 
echo It is going to ask for root password if you didn\'t execute it with root privileges already.
echo
echo Press Enter to continue or Ctrl-C to abort.
read foo

if [ systemctl is-active --quiet sshd ] 
then
	echo *** SSH Server already running, skipped.
else 
	echo *** Install SSH Server 
	install_if(openssh-server)
	echo *** Enable SSH Server 
	sudo systemctl enable ssh
	sudo systemctl start ssh
fi

read foo
if is_installed(network-manager-gnome); 
else 
  echo *** Install Wifi requirements
  sudo apt-get -q install network-manager-gnome
fi

read foo

echo *** if you want to login from network to continue the install script, 
echo *** press Ctrl-C now, set up Wifi if needed 
echo *** then do your remote login and restart the script

#/etc/hostname setzen, anschliessend Reboot?

#NTP einrichten, um die Uhrzeit automatisch einzustellen

#/etc/systemd/timesyncd.conf

echo *** System update. This may take an hour.
sudo apt-get -q update
sudo apt-get -qy upgrade

read foo

echo *** Install Media Player Deamon and Command Line Client
sudo apt-get -q install mpd mpc

read foo

echo *** Install libraries
sudo apt-get -q install git libespeak1 python3-pip 

# TODO Pakete für manuelle Audiosteuerung???

# optional command line tools for GPIO
sudo apt-get -q install gpio-utils

# next may be installed via pip3 too:
sudo apt-get -q install python3-mpd python3-gst-1.0 python3-rpi.gpio
#pip3 install python3-mpd? python3-gst-1.0? python3-rpi.gpio? ???

# must be installed via pip3, no apt-get -q package available
pip3 install pyttsx3

echo *** Install our player script as daemon
sudo cp playerbuttonmonitor.service /etc/sytemd/system
sudo chmod 644 /etc/sytemd/system/playerbuttonmonitor.service
sudo chown root:root /etc/sytemd/system/playerbuttonmonitor.service
sudo systemctl enable playerbuttonmonitor.service
sudo systemctl start playerbuttonmonitor.service



