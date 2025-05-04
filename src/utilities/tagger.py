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
        "Psalm",
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
        "Old Testament",
    ]

    gospel_books = ["Matthew", "Mark", "Luke", "John"]

    johns_epistles = ["I John", "II John", "III John"]

    def is_nativity_reference(ref: str) -> bool:
        """Check if reference is a Nativity passage."""
        ref = ref.strip()

        # Handle specific Matthew references
        if ref.startswith("Matthew 1:"):
            try:
                verse_part = ref.split("Matthew 1:")[1]
                if "-" in verse_part:
                    start, end = map(int, verse_part.split("-"))
                    return start >= 18 and end <= 25
                verse = int(verse_part)
                return 18 <= verse <= 25
            except (ValueError, IndexError):
                return False

        # Handle specific Luke references
        if ref.startswith("Luke 1:") or ref.startswith("Luke 2:"):
            try:
                chapter = int(ref.split("Luke ")[1].split(":")[0])
                return chapter in [1, 2]
            except (ValueError, IndexError):
                return False

        # Handle full chapter references
        return ref == "Matthew 2" or ref == "Luke 1" or ref == "Luke 2"

    for card_key, card_data in card_database.items():
        if not card_data.get("Reference"):
            continue

        # Handle both semicolon separated references and parenthetical references
        references = []

        # First split by semicolons
        for ref_group in card_data["Reference"].split(";"):
            ref_group = ref_group.strip()

            # Check if there are parenthetical references
            if "(" in ref_group and ")" in ref_group:
                # Extract the main reference
                main_ref = ref_group.split("(")[0].strip()
                references.append(main_ref)

                # Extract parenthetical references
                paren_content = ref_group[ref_group.find("(") + 1 : ref_group.find(")")]
                # Split by commas if multiple references in parentheses
                paren_refs = [pr.strip() for pr in paren_content.split(",")]
                references.extend(paren_refs)
            else:
                references.append(ref_group)

        tags = []

        for ref in references:
            # Check for Nativity references
            if is_nativity_reference(ref):
                if "Nativity" not in tags and "Nativity" not in card_data["Identifier"]:
                    tags.append("Nativity")

            # Check for gospel references (excluding John's epistles)
            if any(gospel in ref for gospel in gospel_books) and not any(
                epistle in ref for epistle in johns_epistles
            ):
                if "[Gospel]" not in tags and "[Gospel]" not in card_data["Identifier"]:
                    tags.append("[Gospel]")

            # Determine testament (separate logic from gospel check)
            if any(ot_book in ref for ot_book in ot_books):
                if "[OT]" not in tags and "[OT]" not in card_data["Identifier"]:
                    tags.append("[OT]")
            else:
                if (
                    "[NT]" not in tags
                    and "[NT]" not in card_data["Identifier"]
                    and "O.T." not in card_data.get("Identifier", "")
                ):
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
    # save_card_data(
    #     card_data, "/Applications/LackeyCCG/plugins/Redemption/sets/carddata.txt"
    # )
