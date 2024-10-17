import csv
import random

from src.utilities.tools import load_card_data

PACK_DISTRIBUTIONS = {
    "Israel's Inheritance": {
        "Roots": 5,
        "Israel's Inheritance": {"Rare/Ultra-Rare": 1, "Common": 3},
    },
    "Israel's Rebellion": {
        "Roots": 5,
        "Israel's Rebellion": {"Rare/Ultra-Rare": 1, "Common": 3},
    },
}


def generate_dynamic_filename(pack_weight: dict) -> str:
    sets_involved = "_".join(
        [set_name.replace(" ", "_").lower() for set_name in pack_weight.keys()]
    )
    total_packs = sum(pack_weight.values())
    return f"data/tables/{sets_involved}_{total_packs}_packs.csv"


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


def get_simulations(n_simulations: int, pack_weight: dict):
    """Generate simulations based on pack weight."""
    card_data = load_card_data()
    simulations = []

    for i in range(n_simulations):
        simulation = []
        # Loop through each set and add the corresponding number of packs
        for set_name, num_packs in pack_weight.items():
            for _ in range(num_packs):
                pack = get_pack(set_name, card_data)
                simulation.append(pack)
        simulations.append(simulation)
        print(f"Finished simulation {i + 1}")

    return simulations


if __name__ == "__main__":
    n_simulations = 10_000  # Number of simulations
    pack_weight = {
        "Israel's Inheritance": 3,  # Open 3 packs from this set
        "Israel's Rebellion": 3,  # Open 3 packs from this set
    }

    simulations = get_simulations(n_simulations=n_simulations, pack_weight=pack_weight)
    write_packs_to_csv(generate_dynamic_filename(pack_weight), simulations)
    print("Finished getting packs.")
