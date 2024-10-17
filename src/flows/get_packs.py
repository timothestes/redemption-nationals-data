import csv
import random

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


def write_packs_to_csv(filename: str, packs: list):
    """Write the packs to a CSV file, each card in a separate row."""
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "PK",
                "SimulationNumber",
                "PackNumber",
                "CardName",
                "Rarity",
                "SetName",
                "Brigade",
                "Type",
                "Strength",
                "Toughness",
                "Class",
                "Identifier",
                "Reference",
                "Alignment",
            ]
        )  # Header
        for sim_num, simulation in enumerate(packs, start=1):
            for pack_num, pack in enumerate(simulation, start=1):
                for card in pack:
                    writer.writerow(
                        [
                            f"{sim_num}_{pack_num}_{card['Name']}",
                            sim_num,
                            pack_num,
                            card["Name"],
                            card.get("Rarity", ""),
                            card["OfficialSet"],
                            card["Brigade"],
                            card["Type"],
                            card["Strength"],
                            card["Toughness"],
                            card["Class"],
                            card["Identifier"],
                            card["Reference"],
                            card["Alignment"],
                        ]
                    )


def get_simulations(set_name: str, n_simulations: int, n_packs: int):
    assert (
        set_name in PACK_DISTRIBUTIONS
    ), f"set_name must be in {', '.join(PACK_DISTRIBUTIONS.keys())}"

    card_data = load_card_data()

    simulations = []

    for i in range(n_simulations):
        simulation = []
        for _ in range(n_packs):
            pack = get_pack(set_name, card_data)
            simulation.append(pack)
        simulations.append(simulation)
        print(f"finished simulation {i}")

    return simulations


if __name__ == "__main__":
    n_simulations = 10_000  # Number of simulations
    n_packs = 6  # Number of packs to open per simulation
    set_name = "Israel's Inheritance"
    simulations = get_simulations(
        set_name=set_name, n_simulations=n_simulations, n_packs=n_packs
    )
    write_packs_to_csv(f"data/tables/{set_name.lower()}_packs.csv", simulations)
    print("finished getting packs")
