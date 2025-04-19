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
    """Save the card database to a .txt file, then remove the final CRLF."""
    if not card_database:
        print("Error: Card database is empty")
        return

    first_card = next(iter(card_database.values()))
    terminator = "\r\n"

    with open(card_data_path, "w+", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=first_card.keys(),
            delimiter="\t",
            quoting=csv.QUOTE_NONE,
            escapechar=None,
            quotechar=None,
            lineterminator=terminator,
        )
        writer.writeheader()
        for card in card_database.values():
            writer.writerow(card)
        f.seek(f.tell() - len(terminator))
        f.truncate()


def add_tags(card_database: dict) -> dict:
    """Add scripture reference tags to the Identifier field."""

    ot_books = [
        "Genesis",
        "Exodus",
        "Leviticus",
        "Numbers",
        "Deuteronomy",
        "Joshua",
        "Judges",
        "Ruth",
        "I Samuel",
        "II Samuel",
        "I Kings",
        "II Kings",
        "I Chronicles",
        "II Chronicles",
        "Ezra",
        "Nehemiah",
        "Esther",
        "Job",
        "Psalms",
        "Proverbs",
        "Ecclesiastes",
        "Song of Solomon",
        "Isaiah",
        "Jeremiah",
        "Lamentations",
        "Ezekiel",
        "Daniel",
        "Hosea",
        "Joel",
        "Amos",
        "Obadiah",
        "Jonah",
        "Micah",
        "Nahum",
        "Habakkuk",
        "Zephaniah",
        "Haggai",
        "Zechariah",
        "Malachi",
    ]

    gospel_books = ["Matthew", "Mark", "Luke", "John"]

    johns_epistles = ["I John", "II John", "III John"]

    for card_key, card_data in card_database.items():
        if not card_data.get("Reference"):
            continue

        references = [ref for ref in card_data["Reference"].split(";")]
        tags = []

        for ref in references:
            #  Check for gospel references (excluding John's epistles)
            if any(gospel in ref for gospel in gospel_books) and not any(
                epistle in ref for epistle in johns_epistles
            ):
                if "[Gospel]" not in tags:
                    tags.append("[Gospel]")

            # Check identifier for O.T. first
            if "O.T." in card_data.get("Identifier", ""):
                tags.append("[OT]")
            # Determine testament
            elif any(ot_book in ref for ot_book in ot_books):
                if "[OT]" not in tags:
                    tags.append("[OT]")
            else:
                if "[NT]" not in tags:
                    tags.append("[NT]")

        # Update Identifier field
        if tags:
            current_identifier = card_data["Identifier"].strip()
            tag_string = ",".join(tags)  # No sorting, maintain original order
            card_data["Identifier"] = (
                f"{current_identifier},{tag_string}"
                if current_identifier
                else tag_string
            )

    return card_database


if __name__ == "__main__":
    card_data = load_card_data(CARD_DATA_PATH)
    card_data = add_tags(card_data)
    save_card_data(card_data, CARD_DATA_PATH)
