#!/bin/sh
echo "macOS setup running. This requires Homebrew to be installed. This will take a while and might require some user input."

pip3 install pytradfri --upgrade


brew update
brew install automake fping git


git clone --depth 1 --recursive -b dtls https://github.com/home-assistant/libcoap.git
cd libcoap
./autogen.sh
./configure --disable-documentation --disable-shared --without-debug CFLAGS="-D COAP_DEBUG_FD=stderr"
make
make install
