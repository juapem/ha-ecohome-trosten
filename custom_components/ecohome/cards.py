def hot_water_card(card_list: list) -> dict | None:
    """The hot water tank is reported as the last card, without a mode list."""
    if card_list and card_list[-1].get("modeList") is None:
        return card_list[-1]
    return None


def heating_cards(card_list: list) -> list[dict]:
    """Every card except the hot water tank is a heating zone.

    Only the first zone carries a mode list; on two-zone units the second
    zone is reported without one, just like the hot water tank.
    """
    hot_water = hot_water_card(card_list)
    return [c for c in card_list if c is not hot_water]


def find_card(card_list: list, switch_address: str) -> dict | None:
    return next((c for c in card_list if c.get("switchAddress") == switch_address), None)
