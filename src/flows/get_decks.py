import csv
import os

from prefect import flow, task

from src.schemas.decks import deck_schema
from src.utilities.vars import EVIL_BRIGADES, GOOD_BRIGADES


@task
def get_decklists() -> list:
    decklist_folder = "data/decklists/"
    decklists = [
        os.path.join(decklist_folder, f)
        for f in os.listdir(decklist_folder)
        if f.endswith(".txt")
    ]
    print(f"Found n decklists: {len(decklists)}")
    return decklists


@task
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


def normalize_brigade_field(brigade: str, alignment: str, card_name: str) -> list:
    if not brigade:
        return []

    def handle_complex_brigades(brigade: str) -> list:
        if card_name == "Delivered":
            return ["Green", "Teal", "Evil Gold", "Pale Green"]
        elif card_name == "Eternal Judgment":
            return ["Green", "White", "Brown", "Crimson"]
        elif card_name == "Scapegoat (PoC)":
            return ["Teal", "Green", "Crimson"]
        elif card_name == "Zion":
            return ["Purple"]
        elif card_name == "Ashkelon":
            return ["Good Gold"]
        elif card_name == "Raamses":
            return ["White"]
        elif card_name == "Babel (FoM)":
            return ["Blue"]
        elif card_name == "Sodom & Gomorrah":
            return ["Silver"]
        elif card_name == "City of Enoch":
            return ["Blue"]
        elif card_name == "Hebron":
            return ["Red"]
        elif card_name in ["Damascus (LoC)", "Damascus (Promo)"]:
            return ["Red"]
        elif card_name == "Bethlehem (Promo)":
            return ["White"]
        elif card_name == "Samaria":
            return ["Green"]
        elif card_name == "Nineveh":
            return ["Green"]
        elif card_name == "City of Refuge":
            return ["Teal"]
        elif card_name == "Jerusalem (GoC)":
            return ["Purple", "Good Gold", "White"]
        elif card_name == "Sychar (GoC)":
            return ["Good Gold", "Purple"]
        elif card_name == "Fire Foxes":
            return ["Good Gold", "Crimson", "Black"]
        elif card_name == "Bethlehem (LoC)":
            return ["Good Gold", "White"]

        if "and" in brigade:
            brigade = brigade.split("and")
            return brigade[0].strip().split("/")
        if "(" in brigade:
            main_brigade, sub_brigades = brigade.split(" (")
            sub_brigades = sub_brigades.rstrip(")").split("/")
            if "/" in main_brigade:
                main_brigade = main_brigade.strip().split("/")
            else:
                main_brigade = [main_brigade]
            return main_brigade + sub_brigades
        elif "/" in brigade:
            return brigade.split("/")
        else:
            return [brigade]

    brigades_list = handle_complex_brigades(brigade)

    def replace_gold(brigades, replacement):
        return [replacement if b == "Gold" else b for b in brigades]

    def replace_multi(brigades, replacement):
        return [replacement if b == "Multi" else b for b in brigades]

    if "Multi" in brigades_list:
        if card_name == "Saul/Paul":
            brigades_list = ["Gray", "Good Multi"]
        elif alignment == "Good":
            brigades_list = replace_multi(brigades_list, "Good Multi")
        elif alignment == "Evil":
            brigades_list = replace_multi(brigades_list, "Evil Multi")
        # add handling for exceptions
        elif (
            alignment == "Neutral"
            and card_name == "Unified Language"
            or card_name == "Philosophy"
        ):
            brigades_list = ["Good Multi", "Evil Multi"]
        elif alignment == "Neutral":
            brigades_list = replace_multi(brigades_list, "Good Multi")

    if "Gold" in brigades_list:
        if alignment == "Good":
            brigades_list = replace_gold(brigades_list, "Good Gold")
        elif alignment == "Evil":
            brigades_list = replace_gold(brigades_list, "Evil Gold")
        elif alignment == "Neutral":
            # add gold exceptions
            if brigades_list[0] == "Gold" or card_name in [
                "First Bowl of Wrath (RoJ)",
                "Banks of the Nile/Pharaoh's Court",
            ]:
                brigades_list = replace_gold(brigades_list, "Good Gold")
            else:
                brigades_list = replace_gold(brigades_list, "Evil Gold")
        # if no alignment, assume good gold
        elif not alignment:
            brigades_list = replace_gold(brigades_list, "Good Gold")

    # Add assertions
    allowed_brigades = set(
        GOOD_BRIGADES + EVIL_BRIGADES + ["Good Multi", "Evil Multi", ""]
    )
    for brigade in brigades_list:
        assert (
            brigade in allowed_brigades
        ), f"Card {card_name} has an invalid brigade: {brigade}."

    return brigades_list


@task
def load_decklist(decklist_path: str) -> list:
    with open(decklist_path, "r") as file:
        lines = file.readlines()
    decklist = [line.strip() for line in lines if line.strip()]
    print(f"Loaded decklist from {decklist_path}")
    return decklist


@task
def load_card_data(card_data_path="data/carddata/carddata.txt") -> dict:
    card_data = {}
    with open(card_data_path, "r") as file:
        reader = csv.DictReader(file, delimiter="\t")
        for row in reader:
            card_data[row["Name"]] = row
    print(f"Loaded card data from {card_data_path}")
    return card_data


@task
def write_deck_to_csv(
    deck: list,
    decklist_id: str,
    player_name: str,
    place: int,
    card_data: dict,
    append: bool,
):
    output_dir = "data/decks/"
    os.makedirs(output_dir, exist_ok=True)

    output_file = "data/decks/all_decks.csv"
    if append:
        mode = "a"
    else:
        mode = "w"
    with open(output_file, mode, newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=deck_schema)
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


@flow(log_prints=True)
def get_decks():
    card_data = load_card_data()
    decklists = get_decklists()
    append = False

    for decklist_path in decklists:
        decklist_id = os.path.basename(decklist_path)
        player_name = get_player_name(decklist_id)
        place = get_place(decklist_id)
        deck = load_decklist(decklist_path)
        write_deck_to_csv(deck, decklist_id, player_name, place, card_data, append)
        append = True

    return


if __name__ == "__main__":
    get_decks()
