import csv
import os

from src.schemas.cards import card_schema
from src.utilities.brigades import normalize_brigade_field
from src.utilities.tools import (
    get_decklist_id,
    get_decklists,
    get_place,
    get_player_name,
)


def load_decklist(decklist_path: str) -> list:
    with open(decklist_path, "r") as file:
        lines = file.readlines()
    decklist = [line.strip() for line in lines if line.strip()]
    print(f"Loaded decklist from {decklist_path}")
    return decklist


def load_card_data(card_data_path="data/carddata/carddata.txt") -> dict:
    card_data = {}
    with open(card_data_path, "r") as file:
        reader = csv.DictReader(file, delimiter="\t")
        for row in reader:
            card_data[row["Name"]] = row
    print(f"Loaded card data from {card_data_path}")
    return card_data


def write_cards_to_csv(
    decklist_path: str,
    deck: list,
    card_data: dict,
    append: bool,
):
    decklist_id = get_decklist_id(decklist_path)
    player_name = get_player_name(decklist_id)
    place = get_place(decklist_id)

    output_dir = "data/tables/"
    os.makedirs(output_dir, exist_ok=True)

    output_file = "data/tables/cards.csv"
    if append:
        mode = "a"
    else:
        mode = "w"
    with open(output_file, mode, newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=card_schema)
        in_reserve = False
        writer.writeheader()

        for card in deck:
            # Check if we are entering the "Reserve" or "Tokens" section
            if card.startswith("Reserve:"):
                in_reserve = True
                continue
            elif card.startswith("Tokens:"):
                break

            card_quantity = int(card.split("\t", 1)[0].strip())
            card_name = card.split("\t")[1]
            card_info = card_data.get(card_name, {})
            image_file = card_info.get("ImageFile", "")
            card_id = f"{player_name}_{image_file}"
            brigades = normalize_brigade_field(
                brigade=card_info.get("Brigade"),
                alignment=card_info.get("Alignment"),
                card_name=card_name,
            )

            writer.writerow(
                {
                    "card_id": card_id,  # Primary key: image_file
                    "decklist_id": decklist_id,  # Foreign key: decklist file name
                    "place": place,
                    "player_name": player_name,
                    "quantity": card_quantity,
                    "brigade": brigades,
                    "n_brigades": len(brigades),
                    "card_name": card_name,
                    "in_reserve": in_reserve,
                    "image_file": image_file,
                    "official_set": card_info.get("OfficialSet", ""),
                    "type": card_info.get("Type", ""),
                    "strength": card_info.get("Strength"),
                    "toughness": card_info.get("Toughness"),
                    "class": card_info.get("Class", ""),
                    "identifier": card_info.get("Identifier", ""),
                    "special_ability": card_info.get("SpecialAbility", ""),
                    "rarity": card_info.get("Rarity", ""),
                    "reference": card_info.get("Reference", ""),
                    "alignment": card_info.get("Alignment", ""),
                    "legality": card_info.get("Legality", ""),
                }
            )
    print(f"Deck for {player_name} from {decklist_id} written to {output_file}")


def get_cards():
    card_data = load_card_data()
    decklists = get_decklists()
    append = False

    for decklist_path in decklists:
        deck = load_decklist(decklist_path)
        write_cards_to_csv(decklist_path, deck, card_data, append)
        append = True

    return


if __name__ == "__main__":
    get_cards()
