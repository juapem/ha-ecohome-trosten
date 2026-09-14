from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import ClimateEntityFeature, HVACMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .cards import find_card, heating_cards
from .const import DOMAIN, MANUFACTURER
from .coordinator import EcoHomeCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinators: list[EcoHomeCoordinator] = hass.data[DOMAIN][entry.entry_id]
    entities: list[EcoHomeClimate] = []
    for coordinator in coordinators:
        cards = heating_cards(coordinator.data["detail"]["cardList"])
        for zone, card in enumerate(cards):
            entities.append(EcoHomeClimate(coordinator, card, zone, len(cards)))
    async_add_entities(entities)


class EcoHomeClimate(CoordinatorEntity[EcoHomeCoordinator], ClimateEntity):  # type: ignore[misc]
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_has_entity_name = True

    def __init__(
        self, coordinator: EcoHomeCoordinator, card: dict, zone: int, zone_count: int
    ) -> None:
        super().__init__(coordinator)
        self._switch_address: str = card["switchAddress"]
        self._setting_address: str = card["settingAddress"]
        if zone_count == 1:
            self._attr_name = None  # entity name is the device alias from the app
        else:
            self._attr_name = f"Zone {chr(ord('A') + zone)}"
        # The first zone keeps the id it had before multiple zones were supported.
        suffix = "heating" if zone == 0 else f"heating_{zone + 1}"
        self._attr_unique_id = f"{coordinator.device_code}_{suffix}"
        self._attr_entity_picture = coordinator.device_img_url
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.device_code)},
            name=coordinator.device_name,
            manufacturer=MANUFACTURER,
            model=coordinator.device_model,
        )
        self._update_attrs()

    def _update_attrs(self) -> None:
        detail = self.coordinator.data["detail"]
        unit = detail.get("curUnit", "°C")
        self._attr_temperature_unit = (
            UnitOfTemperature.FAHRENHEIT if unit == "°F" else UnitOfTemperature.CELSIUS
        )
        card = find_card(detail["cardList"], self._switch_address)
        if card is None:
            self._attr_hvac_mode = None
            self._attr_current_temperature = None
            self._attr_target_temperature = None
            return
        self._attr_hvac_mode = HVACMode.HEAT if card["curSwitch"] else HVACMode.OFF
        try:
            self._attr_current_temperature = float(card["curTempMain"])
        except (ValueError, TypeError):
            self._attr_current_temperature = None
        try:
            self._attr_target_temperature = float(card["settingTemp"])
        except (ValueError, TypeError):
            self._attr_target_temperature = None

    def _handle_coordinator_update(self) -> None:
        self._update_attrs()
        self.async_write_ha_state()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        await self.coordinator.async_update_switch_state(
            self._switch_address, hvac_mode == HVACMode.HEAT
        )
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs) -> None:
        if (temp := kwargs.get("temperature")) is None:
            return
        await self.coordinator.async_set_value(self._setting_address, int(temp))
        await self.coordinator.async_request_refresh()
