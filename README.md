# Shelly NG MQTT - Domoticz Python Plugin
Welcome to the ShellyNGMqttPlugin wiki!

## Description
Python plugin for Domoticz to control Shelly Gen 1 **and** Gen2 devices via MQTT. This plugin is based on the originalShellyMQTT - Domoticz Python Plugin of Alexander Nagy/enesbcs (https://github.com/enesbcs/Shelly_MQTT), which is discontinued.

This plugin support Shelly Devices from the first generation (*like the Shelly 2.5 and Shelly Plug, see https://shelly-api-docs.shelly.cloud/gen1/#shelly-family-overview()*) **AND** the second generation (*like the Shelly Plus 2 PM, see https://shelly-api-docs.shelly.cloud/gen2/#, called Shelly NG (Next Gen) - this is still a work in progress*...)

**For Shelly Gen 1 devices:** When MQTT is enabled, the Cloud connection will be disabled and the Shelly devices can't be controlled remotely using the Shelly Smart Control App.

In order to control the Shelly Gen 1 device remotely **and** via Domoticz, see my [Shelly NG HTTP - Domoticz Python Plugin](https://github.com/claskfosmic/ShellyNGHttpPlugin) instead.

## Prerequisites

Tested and works with Domoticz v2024.1

If you do not have a working Python >=3.5 installation, please install it first! (https://www.domoticz.com/wiki/Using_Python_plugins ). If '*Shelly NG Mqtt Plugin*' does not appear in HW list after installation, read again the above article!

Setup and run MQTT broker and an MQTT capable Shelly device. (http://shelly-api-docs.shelly.cloud/#mqtt-support-beta). If you do not have an MQTT server yet, install Mosquitto for example:
http://mosquitto.org/blog/2013/01/mosquitto-debian-repository/.

## Installation

1. Clone repository into your domoticz plugins folder
```
cd domoticz/plugins
git clone https://github.com/claskfosmic/ShellyNGMqttPlugin.git
```
2. Restart domoticz
3. Go to "Hardware" page and add new item with type "ShellyMQTT"
4. Set your MQTT server address and port to plugin settings
5. Remember to allow new devices discovery in Domoticz settings

Once plugin receive any MQTT message from Shelly it will try to create appropriate device.

## Plugin manual update

Warning: if you use this method, Domoticz may duplicate devices after it!

1. Stop domoticz
2. Go to plugin folder and pull new version
```
cd domoticz/plugins/ShellyNGMqttPlugin
git pull
```
3. Start domoticz

## Configuration on your Shelly devices (*use the WebInterface or the Shelly Smart Control App*)

### For Shelly Devices from the first generation, like the Shelly 2.5:
- Enable '*MQTT*' under '*Internet &amp; Security*' -> '*ADVANCED - DEVELOPER SETTINGS*'.
- Do **NOT** use a custom MQTT prefix, the topic should be '*shellies/shellyswitch25-XXXXXXXXXXXX*'.
- ! WARNING: If you enable MQTT - actions via Cloud connection will be disabled!

### For Shelly Devices from the second generation, like the Shelly Plus 2 PM:
- Enable the '*MQTT network*' under '*Settings*' -> 'Connectivity settings' -> '*MQTT*'.
- Make sure the MQTT-prefix starts with 'shellies/', just like the first generation, so the MQTT prefix will look like: '*shellies/shellyplus2pm-XXXXXXXXXXXX*'.
- Do **NOT** change the rest of the prefix, the part '*shellyplus2pm-XXXXXXXXXXXX*' is used to detect the type of device.
- Make sure the options '*Enable "MQTT Control*', '*Enable RPC over MQTT*' and '*RPC status notifications over MQTT*' are enabled.<
- Do **NOT** enable the option 'Generic status update over MQTT', because this will break the energy measurements.

## Supported devices

Based on the original plugin from Alexander Nagy/enesbcs, tested and working with:
 - Shelly 1 Open Source (relay)
 - Shelly 1PM (relay)*
 - Shelly Plug (relay)*
 - Shelly Plug S (relay)*
 - Shelly2 and 2.5 Switch (relay and roller shutter mode, positioning)
 - Shelly4 Pro (relay)*
 - Shelly H&T
 - Shelly RGBW2
 - Shelly Flood
 - Shelly Door and Window sensor
 - Shelly 2LED
 - Shelly Dimmer/Shelly Dimmer2
 - Shelly Bulb RGBW
 - Shelly EM/3EM
 - Shelly Button1
 - Shelly Door Window 2
 - Shelly i3
 - Shelly Bulb Duo
 - Shelly UNI
 - Shelly 1L (relay)
 - Shelly Gas
 - Shelly Motion
 - Shelly Plus H&T (by setting MQTT prefix to `shellies`)

Based on my own tests, everything works for:
 - Gen 1:
   - Shelly 1PM (relay)*
   - Shelly Plug (relay)*
   - Shelly Plug S (relay)*
   - Shelly 2.5 (relay, roller not yet tested)*
   - Shelly Dimmer 2
   - Shelly Color Bulb
   - Shelly Motion
 - Gen 2:
   - Shelly Plus 1 PM
   - Shelly Plus 2 PM
   - Shelly Plus i4

**Power consumption can be enabled in the plugin settings page manually, it's an optional feature without any further support*