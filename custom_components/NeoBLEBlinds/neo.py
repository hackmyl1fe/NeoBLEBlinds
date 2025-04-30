import asyncio
from bleak import BleakClient
import logging
from bleak.backends.device import BLEDevice



from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback



WRITE_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
LOGGER = logging.getLogger(__name__)
header = bytes.fromhex("9a000000")


async def discover():
    """Discover Bluetooth LE devices"""
    devices = await BleakScanner.discover()
    LOGGER.debug("Discoverd devices: %s", [{"address": device.address, "name": device.name} for device in devices])
    return [device for device in devices if device.name.startwith("NEO")]





class NeoInstance:
    def __init__(self, mac: str) ->None:
        self._mac = mac
        self._device = BleakClient(self._mac)
        self._connected = None
        self._current_cover_position = None
        LOGGER.debug("Logger name: %s", __name__)
    
    async def _send(self, data: bytearray):
        LOGGER.debug(''.join(format(x, ' 03x') for x in data))

        if (not self._device.is_connected):
            await self.connect()
        
        await self._device.write_gatt_char(WRITE_UUID, data)
        
        #await asyncio.sleep(2)
        failed = 0
        while(self._connected):
            try:
                LOGGER.debug("Trying to disconnect")
                await self.disconnect()
                break
            except:
                LOGGER.debug("Failed to disconnect")
                if failed == 3: 
                    break
                else: 
                    failed += 1
                    await asyncio.sleep(2)


    async def update(self):
        pass
#    async def stop(self):
#        pass

    @property
    def mac(self):
        return self._mac
    
    async def close_cover(self):
        command = bytes.fromhex("0aeee4")
        await self._send(header + command)
        self._current_cover_position = 0

    async def open_cover(self):
        command = bytes.fromhex("0addd7")
        await self._send(header + command)
        self._current_cover_position = 100

    async def stop_cover(self):
        #Not currently implemented
        #Need to get the real stop command
        command = bytes.fromhex("dddddd")
        await self._send(header + command)

    async def connect(self):
        await self._device.connect(timeout=20)
        #await asyncio.sleep(1)
        self._connected = True
    
    async def disconnect(self):
        if self._device.is_connected:
            await self._device.disconnect()
            self._connected = False
            LOGGER.debug("Disconnected")
    
    async def set_position(self, position):
        """Send the position command to the device."""
        # Implement the actual logic to set the position on your device
        # This could involve sending a command over a network, serial port, etc.
        LOGGER.debug("set the position %s", position)
        self._current_cover_position = position

        #Inverse position to send to blind
        position = 100 - position
        LOGGER.debug("send position %s", position)
        command = bytes.fromhex("dd") + position.to_bytes(1, 'big')
        checksum = self.checksum8_xor(command).to_bytes(1, 'big')

        await self._send(header + command + checksum)

    def update_from_advertisement(self, position):
        """Update position from an advertisment"""
        LOGGER.debug("Advertised position: %s", 100-position)
        self._current_cover_position = 100 - position

    def checksum8_xor(self, data: bytes) -> int:
        """
        Calculates the checksum8 XOR of a byte sequence.

        Args:
            data: The byte sequence to calculate the checksum for.

        Returns:
            The checksum8 XOR value as an integer (0-255).
        """
        checksum = 0
        for byte in data:
            checksum ^= byte
        return checksum & 0xFF
