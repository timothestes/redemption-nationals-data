# This script will add metadata tags to a a .txt file.
import csv
import json

CARD_DATA_PATH = "data/carddata/carddata.txt"


def load_card_data(card_data_path: str) -> dict:
    """Take the data found in 'card_data_path' and load it into a dictionary."""
    card_database = {}
    with open(card_data_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(
            file,
            delimiter="\t",
            quoting=csv.QUOTE_NONE,  # Prevent any automatic quoting
        )
        for row in reader:
            # Preserve the exact string values without any processing
            card_database[f"{row['Name']}____{row['OfficialSet']}"] = {
                k: str(v) if v is not None else "" for k, v in row.items()
            }

    return card_database


def save_card_data(card_database: dict, card_data_path: str) -> None:
    """Save the card database to a .txt file"""
    if not card_database:
        print("Error: Card database is empty")
        return

    first_card = next(iter(card_database.values()))

    with open(card_data_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=first_card.keys(),
            delimiter="\t",
            quoting=csv.QUOTE_NONE,  # Prevent any automatic quoting
            escapechar=None,  # No escape characters
            quotechar=None,  # No quote characters
            lineterminator="\r\n",  # ← enforce CRLF
        )
        writer.writeheader()
        for card in card_database.values():
            writer.writerow(card)


if __name__ == "__main__":
    CARD_DATA = load_card_data(CARD_DATA_PATH)

    with open("tbd.json", "w") as file:
        json.dump(CARD_DATA, file, indent=4)

    save_card_data(CARD_DATA, CARD_DATA_PATH)
