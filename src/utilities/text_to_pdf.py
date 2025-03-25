import os

from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas


def place_section(c, section_data, x, y, line_spacing, add_quantity=True):
    """
    Place sorted items from section_data at (x, y) on the canvas.
    Parameters:
        c: canvas object
        section_data: dictionary of card data
        x: x coordinate
        y: y coordinate
        line_spacing: spacing between lines
        add_quantity: whether to display card quantities
    """
    sorted_items = sorted(section_data.items(), key=lambda item: item[0])
    for card_name, card_data in sorted_items:
        # Handle card names with "/"
        if "/" in card_name:
            # Split on "/" and get the first part
            base_name = card_name.split("/")[0].strip()
            # Check if there's a set name in parentheses in the original name
            if "(" in card_name and ")" in card_name:
                set_name = card_name[card_name.rindex("(") :].strip()
                display_name = f"{base_name} {set_name}"
            else:
                display_name = base_name
        else:
            # Handle Lost Soul cards
            if card_data.get("type") == "Lost Soul" and card_name.startswith(
                "Lost Soul"
            ):
                # Remove "Lost Soul" prefix
                display_name = card_name.replace("Lost Soul ", "", 1)

                # Handle verse references with additional text
                if "[" in display_name:
                    parts = display_name.split("[")
                    base_part = parts[0].strip()
                    verse_part = (
                        parts[1].split("-")[0].strip()
                    )  # Take text before any "-"
                    if verse_part.endswith("]"):
                        display_name = f"{base_part}[{verse_part}"
                    else:
                        display_name = f"{base_part}[{verse_part}]"

                # Keep only the first bracketed reference if multiple exist
                if display_name.count("[") > 1:
                    first_bracket_end = display_name.find("]") + 1
                    display_name = display_name[:first_bracket_end].strip()
            else:
                display_name = card_name

        if add_quantity:
            quantity = card_data.get("quantity", 1)
            display_text = f"{quantity}x {display_name}"
        else:
            display_text = display_name

        c.drawString(x, y, display_text)
        y -= line_spacing


def place_dominants_section(c, main_deck, height_points):
    """
    Place Dominant cards.
    """
    dominants = {k: v for k, v in main_deck.items() if v.get("type") == "Dominant"}
    place_section(c, dominants, 57, height_points - 177, line_spacing=16)


def place_heroes_section(c, main_deck, height_points):
    """
    Place Hero cards.
    """
    heroes = {k: v for k, v in main_deck.items() if v.get("type") == "Hero"}
    place_section(c, heroes, 57, height_points - 545, line_spacing=16)


def place_good_enhancements_section(c, main_deck, height_points):
    """
    Place Good Enhancement (GE) cards.
    """
    good_enh = {k: v for k, v in main_deck.items() if v.get("type") == "GE"}
    place_section(c, good_enh, 54, height_points - 892, line_spacing=16)


def place_lost_souls_section(c, main_deck, height_points):
    """
    Place Lost Soul cards.
    """
    lost_souls = {k: v for k, v in main_deck.items() if v.get("type") == "Lost Soul"}
    place_section(c, lost_souls, 310, height_points - 177, line_spacing=16)


def place_evil_characters_section(c, main_deck, height_points):
    """
    Place Evil Character cards.
    """
    evil_chars = {
        k: v for k, v in main_deck.items() if v.get("type") == "Evil Character"
    }
    place_section(c, evil_chars, 310, height_points - 545, line_spacing=16)


def place_evil_enhancements_section(c, main_deck, height_points):
    """
    Place Evil Enhancement (EE) cards.
    """
    evil_enh = {k: v for k, v in main_deck.items() if v.get("type") == "EE"}
    place_section(c, evil_enh, 310, height_points - 892, line_spacing=16)


def place_artifacts_section(c, main_deck, height_points):
    """
    Place Artifact, Covenant, and Curse cards.
    """
    artifacts = {
        k: v
        for k, v in main_deck.items()
        if v.get("type") in ["Artifact", "Covenant", "Curse"]
    }
    place_section(c, artifacts, 560, height_points - 178, line_spacing=16)


def place_fortresses_section(c, main_deck, height_points):
    """
    Place Fortress and Site cards.
    """
    fortresses = {
        k: v for k, v in main_deck.items() if v.get("type") in ["Fortress", "Site"]
    }
    place_section(c, fortresses, 560, height_points - 471, line_spacing=17)


def place_misc_section(c, main_deck, height_points):
    """
    Place cards that don't fit other categories.
    """
    misc = {
        k: v
        for k, v in main_deck.items()
        if v.get("type")
        not in [
            "Dominant",
            "Hero",
            "GE",
            "Lost Soul",
            "Evil Character",
            "EE",
            "Artifact",
            "Fortress",
            "Site",
            "Curse",
            "Covenant",
        ]
    }
    place_section(c, misc, 560, height_points - 709, line_spacing=17)


def place_reserve_section(c, reserve, height_points):
    """
    Place Reserve cards.
    """
    place_section(
        c, reserve, 580, height_points - 910, line_spacing=16, add_quantity=False
    )


def generate_decklist(deck_data):
    """
    Generate a deck check sheet overlay with multiple sections and
    placeholder text boxes at each corner.
    """
    template_path = "data/pdfs/Type 1 Deck Check Sheet.pdf"
    output_path = "tbd/output_decklist.pdf"
    temp_overlay = "tbd/temp_overlay.pdf"

    reader = PdfReader(template_path)
    page = reader.pages[0]
    width_points = float(page.mediabox.width)
    height_points = float(page.mediabox.height)

    c = canvas.Canvas(temp_overlay, pagesize=(width_points, height_points))

    # Draw placeholder text boxes at each corner
    box_width = 150
    box_height = 30
    margin = 50

    # Top Left
    c.rect(margin, height_points - margin - box_height, box_width, box_height)
    c.drawString(margin + 5, height_points - margin - box_height + 10, "Top Left Box")
    # Top Right
    c.rect(
        width_points - margin - box_width,
        height_points - margin - box_height,
        box_width,
        box_height,
    )
    c.drawString(
        width_points - margin - box_width + 5,
        height_points - margin - box_height + 10,
        "Top Right Box",
    )

    # Place deck sections using positions relative to page height
    main_deck = deck_data.get("main_deck", {})
    reserve = deck_data.get("reserve", {})

    place_dominants_section(c, main_deck, height_points)
    place_heroes_section(c, main_deck, height_points)
    place_good_enhancements_section(c, main_deck, height_points)
    place_lost_souls_section(c, main_deck, height_points)
    place_evil_characters_section(c, main_deck, height_points)
    place_evil_enhancements_section(c, main_deck, height_points)
    place_artifacts_section(c, main_deck, height_points)
    place_fortresses_section(c, main_deck, height_points)
    place_misc_section(c, main_deck, height_points)
    place_reserve_section(c, reserve, height_points)

    c.showPage()
    c.save()

    overlay_pdf = PdfReader(temp_overlay)
    if overlay_pdf.pages:
        page.merge_page(overlay_pdf.pages[0])
    writer = PdfWriter()
    writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)
    os.remove(temp_overlay)


if __name__ == "__main__":
    import json

    with open("tbd/deck_data.json", "r") as f:
        deck_data = json.load(f)
    generate_decklist(deck_data)
