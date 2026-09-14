import pytest
from homeassistant.components.climate.const import HVACMode
from homeassistant.helpers import entity_registry as er

from custom_components.ecohome.const import DOMAIN

from .conftest import DEVICE_CODE

# A two-zone unit: only zone A has a mode list, zone B and the hot water tank don't.
TWO_ZONE_DETAIL = {
    "curUnit": "℃",
    "cardList": [
        {
            "card": "0",
            "switchAddress": "1574",
            "curSwitch": True,
            "curTempMain": "43.5",
            "settingTemp": "65.0",
            "settingAddress": "1003",
            "modeList": [{"modeAddress": "1001", "modeValue": "2", "modeMeaning": "Verwarming"}],
        },
        {
            "card": "1",
            "switchAddress": "1575",
            "curSwitch": False,
            "curTempMain": "31.0",
            "settingTemp": "40.0",
            "settingAddress": "1007",
            "modeList": None,
        },
        {
            "card": "2",
            "switchAddress": "1576",
            "curSwitch": True,
            "curTempMain": "60.4",
            "settingTemp": "55.0",
            "settingAddress": "1004",
            "modeList": None,
        },
    ],
}


@pytest.fixture
async def setup_two_zones(hass, config_entry, mock_login):
    mock_login.get_device_detail.return_value = TWO_ZONE_DETAIL
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    return config_entry


def _entity_id(hass, platform, suffix):
    return er.async_get(hass).async_get_entity_id(platform, DOMAIN, f"{DEVICE_CODE}_{suffix}")


async def test_both_zones_are_climate_entities(hass, setup_two_zones):
    zone_a = hass.states.get(_entity_id(hass, "climate", "heating"))
    zone_b = hass.states.get(_entity_id(hass, "climate", "heating_2"))

    assert zone_a.name.endswith("Zone A")
    assert zone_a.state == HVACMode.HEAT
    assert zone_a.attributes["current_temperature"] == 43.5

    assert zone_b.name.endswith("Zone B")
    assert zone_b.state == HVACMode.OFF
    assert zone_b.attributes["current_temperature"] == 31.0
    assert zone_b.attributes["temperature"] == 40.0


async def test_hot_water_is_the_last_card(hass, setup_two_zones):
    state = hass.states.get(_entity_id(hass, "water_heater", "hot_water"))

    assert state.attributes["current_temperature"] == 60.4
    assert state.attributes["temperature"] == 55.0


async def test_zone_b_set_temperature(hass, setup_two_zones, mock_login):
    await hass.services.async_call(
        "climate", "set_temperature",
        {"entity_id": _entity_id(hass, "climate", "heating_2"), "temperature": 35},
        blocking=True,
    )

    mock_login.set_value.assert_awaited_once_with(DEVICE_CODE, "1007", 35)
