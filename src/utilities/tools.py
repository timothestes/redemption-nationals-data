import csv
import os

from src.utilities.brigades import normalize_brigade_field


def load_card_data(card_data_path="data/carddata/carddata.txt") -> dict:
    card_data = {}
    with open(card_data_path, "r") as file:
        reader = csv.DictReader(file, delimiter="\t")
        for row in reader:
            card_data[row["Name"]] = row
            card_data[row["Name"]]["Brigade"] = normalize_brigade_field(
                brigade=card_data[row["Name"]].get("Brigade"),
                alignment=card_data[row["Name"]].get("Alignment"),
                card_name=row["Name"],
            )
    print(f"Loaded card data from {card_data_path}")
    return card_data


def get_player_name(decklist_id: str) -> str:
    return (
        decklist_id.split("_")[2] + "_" + decklist_id.split("_")[3].replace(".txt", "")
    )


def get_place(decklist_id: str) -> int:
    parts = decklist_id.split("_")

    if len(parts) >= 2:
        place_str = parts[1]
        place_numeric = "".join(filter(str.isdigit, place_str))
        return int(place_numeric) if place_numeric else None
    else:
        return None


def get_decklists() -> list:
    decklist_folder = "data/decklists/"
    decklists = [
        os.path.join(decklist_folder, f)
        for f in os.listdir(decklist_folder)
        if f.endswith(".txt")
    ]
    return sorted(decklists)


def get_decklist_id(decklist_path) -> str:
    return os.path.basename(decklist_path)
