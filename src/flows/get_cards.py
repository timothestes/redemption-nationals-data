import csv
import os

from src.schemas.cards import card_schema
from src.utilities.tools import (
    get_decklist_id,
    get_decklists,
    get_place,
    get_player_name,
    load_card_data,
)


def load_decklist(decklist_path: str) -> list:
    with open(decklist_path, "r") as file:
        lines = file.readlines()
    decklist = [line.strip() for line in lines if line.strip()]
    print(f"Loaded decklist from {decklist_path}")
    return decklist


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

    output_file = "data/tables/cards3.csv"
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
            original_card_id = card_id
            for n in range(0, card_quantity):
                if n > 0:
                    card_id = f"{original_card_id}_{n}"
                writer.writerow(
                    {
                        "card_id": card_id,  # Primary key: image_file
                        "decklist_id": decklist_id,  # Foreign key: decklist file name
                        "place": place,
                        "player_name": player_name,
                        "brigade": card_data.get("Brigade"),
                        "n_brigades": len(card_data.get("Brigade")),
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
