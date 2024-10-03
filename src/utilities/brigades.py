from src.utilities.vars import EVIL_BRIGADES, GOOD_BRIGADES


def handle_complex_brigades(card_name: str, brigade: str) -> list:
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
    elif card_name == "New Jerusalem (Bride of Christ) (RoJ AB)":
        return GOOD_BRIGADES

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


def replace_gold(brigades, replacement):
    return [replacement if b == "Gold" else b for b in brigades]


def replace_multi(brigades, replacement):
    return [replacement if b == "Multi" else b for b in brigades]


def replace_multi_brigades(brigades_list: list) -> list:
    # Replace "Good Multi" with GOOD_BRIGADES if present
    if "Good Multi" in brigades_list:
        brigades_list = [
            brigade for brigade in brigades_list if brigade != "Good Multi"
        ]
        brigades_list.extend(GOOD_BRIGADES)

    # Replace "Evil Multi" with EVIL_BRIGADES if present
    if "Evil Multi" in brigades_list:
        brigades_list = [
            brigade for brigade in brigades_list if brigade != "Evil Multi"
        ]
        brigades_list.extend(EVIL_BRIGADES)

    return brigades_list


def handle_gold_brigade(card_name, alignment, brigades_list):
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

    return brigades_list


def normalize_brigade_field(brigade: str, alignment: str, card_name: str) -> list:
    if not brigade:
        return []

    brigades_list = handle_complex_brigades(card_name, brigade)

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
        brigades_list = handle_gold_brigade(card_name, alignment, brigades_list)

    brigades_list = replace_multi_brigades(brigades_list)
    allowed_brigades = set(GOOD_BRIGADES + EVIL_BRIGADES)
    for brigade in brigades_list:
        assert (
            brigade in allowed_brigades
        ), f"Card {card_name} has an invalid brigade: {brigade}."

    return brigades_list
