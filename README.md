# Onæri Trådfri
Controller for the Ikea Trådfri line of smart lights based on the Onæri principles. This is an extra command layer on top of the existing ones with the goal of improving the user's sleep rhythm.

Onæri Trådfri is an implementation of [Onaeri](https://github.com/Lakitna/Onaeri) built upon [Pytradfri](https://github.com/ggravlingen/pytradfri).


## Features
- Onæri chronocycle
  - Wake-up phase
  - Active phase
  - Sleep prepare phase
- Run multiple cycles, each with their own settings


## Installation
This controller requires a device with a local network interface (WiFi or Ethernet) that can run Python. For example a Linux pc (like Raspberry Pi), a Windows pc or a macOS pc. Make sure the device running the controller will not go into sleep mode as it will disrupt the program.

At this point, this controller requires the user to know the basics of running Python programs using the command line. This will hopefully change in the future.

### 1. Install Pytradfri
Install the [Pytradfri](https://github.com/ggravlingen/pytradfri) module with the following command:

    $ pip3 install pytradfri

If this gives an error try the following:

    $ sudo pip3 install pytradfri

### 2. Download
Download all the files in this repository and place it in a convenient location.

### 3. Change settings
Change the settings in the `settings` folder

1. In `Global.py` add the details to your gateway (`gatewayIp` and `gatewayKey`)
2. Create a cycle by making a new settings file using `Template.py` as a template. For example name it `Bedroom.py`.
3. Change your bedtime (`userAlarmTime`) and waketime (`userSleepTime`) in the new `Bedroom.py` settings file.
4. Using the official Ikea Trådfri app change the names of your lamps to include the name of the settings file you made in the previous steps. In our example you could name one light `Bedroom ceiling` and another lamp could be `bedroom nightstand`.

### 4. Run it
Run Onaeri.py using the following command, but don't forget to `cd` to the correct folder first:

    $ python3 Onaeri.py


## Contributing
Feel free to contribute, adapt & repurpose for any purpose, including commercial use. Just make sure you adhere to basic Github conventions :)
