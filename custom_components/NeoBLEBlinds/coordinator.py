import logging
from typing import TYPE_CHECKING

from homeassistant.components import bluetooth
from homeassistant.components.bluetooth.passive_update_coordinator import (
    PassiveBluetoothDataUpdateCoordinator
)
from homeassistant.core import CoreState, HomeAssistant, callback
from .neo import NeoInstance

#if TYPE_CHECKING:
from bleak.backends.device import BLEDevice
_LOGGER = logging.getLogger(__name__)
neo_uuid = "0000180f-0000-1000-8000-00805f9b34fb"
class PassiveBtCoordinator(PassiveBluetoothDataUpdateCoordinator):
    
    """Class to manage fetching example data."""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        ble_device: BLEDevice,
        base_unique_id: str,
        device: NeoInstance
    ) -> None:

        """Initialize example data coordinator."""
        self.data: dict[str, Any] = {}
        self.ble_device = ble_device
        self.base_unique_id = base_unique_id
        _LOGGER.debug("Neo-Blind coordinator: %s", self.ble_device.address)
        super().__init__(
            hass=hass,
            logger=logger,
            address=ble_device.address,
            mode=bluetooth.BluetoothScanningMode.ACTIVE,
            connectable=True,
        )

        self.device = device

    @callback
    def _async_handle_unavailable(
        self, service_info: bluetooth.BluetoothServiceInfoBleak
    ) -> None:
        """Handle the device going unavailable."""

    @callback
    def _async_handle_bluetooth_event(
        self,
        service_info: bluetooth.BluetoothServiceInfoBleak,
        change: bluetooth.BluetoothChange,
    ) -> None:
        """Handle a Bluetooth event."""
        # Your device should process incoming advertisement data
        
        _LOGGER.debug("Got some update")
        #if adv := parse_advertisement_data(
        #    service_info.device, service_info.advertisement
        #):
        
        self.data = service_info.advertisement
        self.device.update_from_advertisement(list(self.data.service_data[neo_uuid])[1])
        _LOGGER.debug("%s: Neo-Blind data: %s", self.ble_device.address, list(self.data.service_data[neo_uuid]))
        #self.api.update_from_advertisement(adv)
        super()._async_handle_bluetooth_event(service_info, change)