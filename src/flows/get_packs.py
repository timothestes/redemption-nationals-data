import random

from src.utilities.brigades import normalize_brigade_field
from src.utilities.tools import load_card_data

PACK_DISTRIBUTIONS = {
    "Israel's Inheritance": {
        "Roots": 5,
        "Israel's Inheritance": {"Rare/Ultra-Rare": 1, "Common": 3},
    }
}


def save_to_json(filename: str, data: dict):
    import json

    with open(filename, "w") as f:
        f.write(json.dumps(data, indent=4))


def get_cards_by_rarity(card_set: str, rarity: str, card_data: dict) -> list[dict]:
    """Retrieve cards by rarity from a specific card set."""
    return [
        card
        for card in card_data.values()
        if card["OfficialSet"] == card_set and card.get("Rarity") == rarity
    ]


def get_rare_ultra_rare_cards(card_set: str, card_data: dict) -> list[dict]:
    """Retrieve cards that are either Rare or Ultra-Rare from a specific card set."""
    return [
        card
        for card in card_data.values()
        if card["OfficialSet"] == card_set and card["Rarity"] in ["Rare", "Ultra-Rare"]
    ]


def get_cards_without_rarity(card_set: str, card_data: dict) -> list[dict]:
    """Retrieve cards that do not have a rarity (like Roots)."""
    return [card for card in card_data.values() if card["OfficialSet"] == card_set]


def get_pack(set_name: str, card_data: dict) -> list[dict]:
    """Create a single pack of cards based on the set name and card distribution."""
    pack = []
    distributions = PACK_DISTRIBUTIONS[set_name]

    for card_set, rarity_distribution in distributions.items():
        if isinstance(rarity_distribution, dict):
            for rarity, count in rarity_distribution.items():
                if rarity == "Rare/Ultra-Rare":
                    rare_ultra_rare_cards = get_rare_ultra_rare_cards(
                        card_set, card_data
                    )
                    pack.extend(random.sample(rare_ultra_rare_cards, 1))
                else:
                    filtered_cards = get_cards_by_rarity(card_set, rarity, card_data)
                    pack.extend(random.sample(filtered_cards, count))
        else:
            # Handle sets like "Roots" that don't have card rarities
            filtered_cards = get_cards_without_rarity(card_set, card_data)
            pack.extend(random.sample(filtered_cards, rarity_distribution))

    return pack


def get_packs(set_name: str, n_packs: int):
    assert (
        set_name in PACK_DISTRIBUTIONS
    ), f"set_name must be in {', '.join(PACK_DISTRIBUTIONS.keys())}"

    card_data = load_card_data()

    packs = []

    save_to_json("tbd.json", card_data)

    for i in range(1, n_packs + 1):
        packs.append(get_pack(set_name, card_data))


if __name__ == "__main__":
    get_packs(set_name="Israel's Inheritance", n_packs=1)
