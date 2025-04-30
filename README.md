# NeoBLEBlinds
Neo Blinds Bluetooth integration for Home Assistant

This integration is to control Neo Bluetooth blinds that are controlled thorugh their [Bluelink](https://neosmartblinds.com/bluelink/) app
This [Home Assistant](https://www.home-assistant.io) integration will allow you to manage your blind without the app
They dont provide a solution to manage bluetooth blinds through a hub so i created this HA integration

*Note i've only tested this integration running on a RPi 4 using the integrated bluetooth adapter

## Installation

1. Install [HACS](https://www.hacs.xyz/docs/use/configuration/basic/)
2. Once installed add this custom repo through HACS
3. Search for `Neo`
4. Click download for the Neo BLE Blinds integration
5. Restart Home Assistant

## Configuration is done in the UI

If the blinds are within range they should automatically be discovered under devices
