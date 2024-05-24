
# Sensortile.boxPro Retrieve data from USB and send them via MQTT

This project consists of two scripts designed to be used on both Windows PC and Raspberry Pi (specifically tested on Raspberry Pi 3B/4B). These scripts facilitate the connection to a Sensortile.box Pro device to retrieve sensor data, process it, and transmit it to a user interface developed in Node-RED via MQTT.
The python script takes care to manage exceptions that could be raised if the SensorTile is shut down or disconnected from the USB port, so that it can continue to run and resume when the device comes back.
It also manages network disconnections.
Improvements in the mqtt client in order to manage also the QoS parameter.
The new version also sends to the MQTT server the SensorTile timestamp associated to each data frame. Since the SensorTile RTC looses correct date/time settings at each power off, the timestamp are properly corrected based on the time provided by a NTP server.

## Table of Content
- [Dependencies](#dependencies)
- [Setup](#setup)
- [Usage](#usage)
  
## Dependencies

Before proceeding with the installation, make sure you have the following dependencies installed:

- Python (recommended version: >=3.6)
  ```bash
    sudo apt-get python3
- Nodered (follow the instruction in the official site)
  
### Python Libraries

The following Python libraries need to be installed:

- [paho-mqtt](https://pypi.org/project/paho-mqtt/)
  ```bash
    sudo pip3 install "paho-mqtt<2"
  ```
- Using RPI: [pyusb](https://pypi.org/project/pyusb/)
    ```bash
    sudo pip3 install pyusb
- [ntplib](https://pypi.org/project/ntplib/)
		```bash
		sudo pip3 install ntplib

The following libraries are required to obtain an ID for the SensorTile. They can work only if the BTLE connection is enabled.
Improvements are necessary in the case multiple SensorTile are present in the area or are connected via USB to the same RPi
- [bleak](https://pypi.org/project/bleak/)
		```bash
		sudo pip3 install bleak
- [asyncio](https://pypi.org/project/asyncio/)
		```bash
		sudo pip3 install asyncio
		
### Nodered Library

Install the node-red-dashboard library by running the following command in your Node-RED installation directory:
```bash
npm install node-red-dashboard
```

## Setup

### Sensortile Setup

To set up the Sensortile.box Pro for data collection, follow these steps:

1. Connect to the Sensortile using the ST BLE Sensor app on your mobile device.
2. Start a new flow that outputs temperature, low power accelerometer and accelerometer data via USB upload the file inside the zip "usbflow.js"
   
### Modify setup Rpi

To configure the Raspberry Pi for the Sensortile, follow these steps:

1. Check the ID product and ID vendor of the Sensortile by running the command `lsusb`. For example, in a line like this: "Bus 001 Device 004: ID 0483:5740 STMicroelectronics Virtual COM Port",   `idVendor=0483` and `idProduct=5740`.
2. Once you have checked this information, run the command `sudo nano /etc/udev/rules.d/99-com.rules` to open the file in the terminal.
3. Modify the file by adding the following line: `SUBSYSTEMS=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5740", GROUP="users", MODE="0666"`, replacing the idVendor and idProduct values with the ones you checked earlier.
4. Save the file
5. Modify the file `usb_rpi_conncection.py` with the correct ids and the usefull topic that you want to use in mqtt
### Nodered Setup

To set up Node-RED, follow these steps:

1. Download the JSON file `flows.json`.
2. Import the downloaded file into Node-RED. Within it, there will be a graphical interface to interact with.
3. Modify the flow inserting the same topic chosen before
## Usage

### Usage on Raspberry Pi

To use the scripts on Raspberry Pi, follow these steps:

1. [Modify setup Rpi](#modify-setup-rpi) as described above.
2. Run the script using Python:
```bash
  python3 usb_rpi_conncection.py
```
You will see all the data in terminal and in UI of Nodered
### Usage on Windows
To use the scripts on Windows, follow these steps:
1. Verify the COM port in wich the sensortile is connected, than change it in the file `main`
2. Run the python code
You will see all the data in terminal and in UI of Nodered
