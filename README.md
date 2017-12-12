# Onæri Trådfri
Controller for the Ikea Trådfri line of smart lights based on the Onæri principles. This is an extra command layer on top of the existing ones with the goal of improving the user's sleep rhythm.

Onæri Trådfri is an implementation of [Onæri](https://github.com/Lakitna/Onaeri) built upon [Pytradfri](https://github.com/ggravlingen/pytradfri).


## Features
- Onæri chronocycle
  - Wake-up phase
  - Active phase
  - Sleep prepare phase
- Run multiple cycles, each with their own settings
- Temporary deviate from a cycle using the normal Trådfri controls


## Installation
This controller requires a device with a local network interface (WiFi or Ethernet) that can run Python. For example a Linux pc (like Raspberry Pi), a Windows pc or a macOS pc. Make sure the device running the controller will not go into sleep mode as it will disrupt the program.

At this point, this controller requires the user to know the basics of running Python programs using the command line. This will hopefully change in the future.

### 1. Download
1. Download all the files from this repository and place it in a convenient location.
2. Proceed to download the files from the [Onaeri API repository](https://github.com/Lakitna/Onaeri) and place the files inside the `Onaeri` folder.

Or just run the following command and let the computer do all the hard work:

    git clone https://github.com/Lakitna/Onaeri-tradfri.git --recurse-submodules


### 2. Run installer
Locate the file `setup_linux.sh` or `setup_macos.sh` and execute them. Unfortunately there is no Windows installer yet.

Run the correct setup file and watch the magic happen. The setup will install all dependencies for you, this will take a while.


### 3. Change settings
Change the settings in the folder `Onaeri/settings`

1. Create a cycle by making a new settings file using `Template.py` as a template. For example name it `Bedroom.py`.
2. Change your bedtime (`alarmTime`), waketime (`sleepTime`), and possibly other settings in the new `Bedroom.py` settings file.
3. Using the official Ikea Trådfri app change the names of your lamps to include the name of the settings file you made in the previous steps. In our example you could name one light `Bedroom ceiling` and another lamp in the same cycle could be `bedroom nightstand`.


### 4. Run it
Run Onaeri.py using the following command, but don't forget to `cd` to the correct parent folder first:

    $ python3 Onaeri-tradfri


## Contributing
Feel free to contribute, adapt & repurpose for any purpose, including commercial use. Just make sure you adhere to basic Github conventions :)
