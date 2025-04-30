"""Platform for Cover Intergration"""
from __future__ import annotations

import logging 

from .neo import NeoInstance 
from .coordinator import PassiveBtCoordinator
from .btentity import GenericBTEntity
from .const import DOMAIN
import voluptuous as vol 

from pprint import pformat

#Import cover related things
import homeassistant.helpers.config_validation as cv
from homeassistant.components.cover import (
    PLATFORM_SCHEMA,
    DEVICE_CLASSES_SCHEMA,
    ATTR_POSITION,
    CoverEntityFeature,
    CoverDeviceClass,
    CoverEntity
)
from homeassistant.const import CONF_NAME, CONF_ADDRESS
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.core import CoreState, HomeAssistant, callback

_LOGGER = logging.getLogger(__name__)


#Validation of the user's config
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME): cv.string,
    vol.Required(CONF_ADDRESS): cv.string,
})

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
    ) -> None:

    """Setup Neo blinds"""
    #Add devices
    _LOGGER.info(pformat(config))

    cover = {
        "name": config[CONF_NAME],
        "mac": config[CONF_ADDRESS]
    }

    add_entities([NeoBlind(cover)])

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Generic BT device based on a config entry."""
    coordinator: PassiveBtCoordinator = hass.data[DOMAIN][entry.entry_id]
    cover = {
        "name": entry.data[CONF_NAME],
        "mac": entry.data[CONF_ADDRESS]
    }
    _LOGGER.debug("Neo-Blind coordinator: %s", coordinator.ble_device.address)
    async_add_entities([NeoBlind(coordinator, cover)])

    #platform = entity_platform.async_get_current_platform()
    #platform.async_register_entity_service("write_gatt", Schema.WRITE_GATT.value, "write_gatt")
    #platform.async_register_entity_service("read_gatt", Schema.READ_GATT.value, "read_gatt")


class NeoBlind(CoverEntity, GenericBTEntity):
    """Representation of a NeoBlind"""
    _attr_device_class = CoverDeviceClass.BLIND

    def __init__(self, coordinator: PassiveBtCoordinator, cover) -> None:
        """init neo blind"""
        _LOGGER.info(pformat(cover))
        self._name = cover["name"]
        self._device_class = CoverDeviceClass.BLIND
        self._attr_supported_features = CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.SET_POSITION
        super().__init__(coordinator)

    @property
    def supported_features(self):
        """Flag supported features."""
        return self._attr_supported_features

    @property
    def device_class(self):
        """Return the device class of the cover."""
        return self._device_class

    @property
    def name(self) -> str:
        """Return the display name of this blind"""
        return self._name
    
    @property
    def is_closed(self) -> bool | None:
        """Return state of blind - return true if is closed"""
        if self._device._current_cover_position is None:
            return None
        return self._device._current_cover_position == 0

    @property
    def current_cover_position(self) -> int | None:
        """Return current position of cover.

        None is unknown, 0 is Closed, 100 is open.
        """
        if self._device._current_cover_position is None:
            return None
        return self._device._current_cover_position

    async def async_close_cover(self, **kwargs):
        """Close cover."""
        await self._device.close_cover()
        _LOGGER.debug("Asked for close: %s", self._device._current_cover_position)
        self.async_write_ha_state()

    async def async_open_cover(self, **kwargs):
        """Open the cover."""
        await self._device.open_cover()
        _LOGGER.debug("Asked for open - state: %s", self._device._current_cover_position)
        self.async_write_ha_state()

    #async def async_stop_cover(self, **kwargs):
    #    """Stop the cover."""    
    #    await self._device.stop_cover()
    #    self.async_write_ha_state()

    #def update(self):
    #    pass
    
    async def async_set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        position = kwargs[ATTR_POSITION]
        if position is not None:
            # Implement the logic to set the cover position
            # For example, send a command to your device to set the position
            await self._device.set_position(position)
            self.async_write_ha_state()
