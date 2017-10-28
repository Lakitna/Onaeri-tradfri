# Onæri Trådfri

Controller for the Ikea Trådfri line of smart lights based on the Onæri principles. This is an extra command layer on top of the existing ones with the goal of improving the user's sleep rhythm. 

## Features

- Onæri chronocycle
  - Wake-up phase
  - Active phase
  - Sleep prepare phase

## Installation

This controller requires a device with a local network interface (WiFi or Ethernet) that can run Python. For example [Any Raspberry Pi](https://www.raspberrypi.org/products/) (provided it has a network interface), any Linux pc, any Windows pc or any MacOs pc. Make sure the device running the controller will not go into sleep mode as it will disrupt the program.

Onæri Trådfri is built upon [Pytradfri](https://github.com/ggravlingen/pytradfri). 

At this point, this controller requires the user to know the basics of running Python programs using the command line. This will hopefully change in the future.

1. Follow the installation instructions for synchronous functionality at the [Pytradfri page](https://github.com/ggravlingen/pytradfri).
2. Add the contents of this repository to the Pytradfri folder
3. Change the settings in Settings.py
   - Add the details to your gateway (`gatewayIp` and `gatewayKey`)
   - Set your bed- and waketime (`userAlarmTime` and `userSleepTime`)
4. Run Onaeri.py and observe the awesomeness

## Contributing
Feel free to contribute, adapt & repurpose for any purpose, including commercial use. Just make sure you adhere to basic Github conventions :)
