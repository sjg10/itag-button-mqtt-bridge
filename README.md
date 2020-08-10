
# iTAG Button <-> MQTT Bridge

## Description
The iTAG is a very cheap Bluetooth Low Energy (BLE) button that can be used for IoT setups. It is usually used with the iSearching app. The following is a python application to bridge a button to perform a set of publishes when pressed.

This program instead can be run on any device supporting Bluetooth LE (such as a Raspberry Pi 3 or 4) and communicates over MQTT for control and monitoring of the device.

## Background and License
Licensed under the GPLv3.

## Requirements

 - Docker compose
 - An MQTT server/broker.

For one time setup you also require:

 - Python 3 and pip

## Setup 
### New device
To connect a new device one time setup must be performed:

 1. Insert a battery and turn on the device as per the manufacturer instructions.
 1. On the host machine, install the python requirements with `pip3 install -r requirements`
 1. Run `python3 onetimesetup.py`. This will detect the available nearby devices, and you can make a note of your device's MAC address.

### Config File
To start the server a config file `vars.env` must be filled on, by copying and completing the template `vars.env.eg`. The fields are as follows:

|Variable|Description  |
|--|--|
|BUTTON_MAC|The MAC address of the button, obtained in the one time setup step above.|
|DEVICE_NAME|A human readable name that will form the MQTT topic used.|
|MQTT_USERNAME|The username of your local mqtt server|
|MQTT_PASSWORD|The password for your local mqtt server|
|MQTT_ADDRESS|The address of your local mqtt server. Note even if this is the same machine use the absolute IP not localhost, as docker point localhost inside itself, not to the host machine|
|MQTT_PORT|The port of your local mqtt server (typically 1883)|
|DEFAULT_TOPIC|The default MQTT topic to publish to when the button is pressed|
|DEFAULT_MSG|The default MQTT payload to publish to when the button is pressed|


## Running
Run a `docker-compose build` followed by `docker-compose up -d` to run and register the service to always restart. Use docker compose to control and monitor the app (https://docs.docker.com/compose/)

Create copies of `vars.env` and add further services to the `docker-compose.yml` to manage multiple devices.

## MQTT Interface

Once running the following subtopics are available:

- `DEVICE_NAME/targets`: Publish here to override the topics that the button will publish to. Must be JSON with an attribute `targets` that forms an array of elements with the attributes `topic` and `msg`
- `DEVICE_NAME/status` : Publish here any payload to request a battery status update.
- `DEVICE_NAME/bat`: Provides battery level as a percentage. Is updated when `DEVICE_NAME/status` receives a message.

