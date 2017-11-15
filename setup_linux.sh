#!/bin/sh
echo "Linux setup running. This will take a while and might require some user input."

sudo pip3 install pytradfri --upgrade


sudo apt-get update
sudo apt-get install autoconf automake libtool, m4 fping git


git clone --depth 1 --recursive -b dtls https://github.com/home-assistant/libcoap.git
cd libcoap
./autogen.sh
./configure --disable-documentation --disable-shared --without-debug CFLAGS="-D COAP_DEBUG_FD=stderr"
sudo make
sudo make install
