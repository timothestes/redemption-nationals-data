import os
import re

from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas


def clean_card_name(card_name, card_data):
    """
    Clean the card name using regex.
    - If the name contains a '/', take the part before it and append any trailing set name in parentheses.
    - For Lost Soul cards, remove the "Lost Soul " prefix and any hyphenated text inside brackets.
    """
    if "/" in card_name:
        base_name = card_name.split("/")[0].strip()
        match = re.search(r"(\([^)]*\))\s*$", card_name)
        if match:
            return f"{base_name} {match.group(1).strip()}"
        return base_name

    if card_data.get("type") == "Lost Soul" and card_name.startswith("Lost Soul"):
        display_name = re.sub(r"^Lost Soul\s+", "", card_name)

        def bracket_repl(match):
            inner = match.group(1)
            inner_clean = re.sub(r"\s*-\s*[^]]+", "", inner)
            return f"[{inner_clean.strip()}]"

        display_name = re.sub(r"\[([^\]]+)\]", bracket_repl, display_name)
        first_bracket = re.search(r"\[[^\]]+\]", display_name)
        if first_bracket:
            display_name = display_name[: first_bracket.end()].strip()
        return display_name

    return card_name


def place_section(c, section_data, x, y, line_spacing, add_quantity=True):
    """
    Place sorted items from section_data at (x, y) on the canvas.
    """
    sorted_items = sorted(section_data.items(), key=lambda item: item[0])
    for card_name, card_data in sorted_items:
        display_name = clean_card_name(card_name, card_data)
        if add_quantity:
            quantity = card_data.get("quantity", 1)
            display_text = f"{quantity}x {display_name}"
        else:
            display_text = display_name
        c.drawString(x, y, display_text)
        y -= line_spacing


def draw_count(c, section_data, x, y, font="Helvetica", font_size=12):
    """
    Draw just the total count (number) for section_data at (x, y).
    """
    total = sum(int(card.get("quantity", 1)) for card in section_data.values())
    c.setFont(font, font_size)
    c.drawString(x, y, str(total))


def place_dominants_section(c, main_deck, height_points):
    dominants = {k: v for k, v in main_deck.items() if v.get("type") == "Dominant"}
    place_section(c, dominants, 57, height_points - 177, line_spacing=16)


def place_heroes_section(c, main_deck, height_points):
    heroes = {k: v for k, v in main_deck.items() if v.get("type") == "Hero"}
    place_section(c, heroes, 57, height_points - 545, line_spacing=16)


def place_good_enhancements_section(c, main_deck, height_points):
    good_enh = {k: v for k, v in main_deck.items() if v.get("type") == "GE"}
    place_section(c, good_enh, 54, height_points - 892, line_spacing=16)


def place_lost_souls_section(c, main_deck, height_points):
    lost_souls = {k: v for k, v in main_deck.items() if v.get("type") == "Lost Soul"}
    place_section(c, lost_souls, 310, height_points - 177, line_spacing=16)


def place_evil_characters_section(c, main_deck, height_points):
    evil_chars = {
        k: v for k, v in main_deck.items() if v.get("type") == "Evil Character"
    }
    place_section(c, evil_chars, 310, height_points - 545, line_spacing=16)


def place_evil_enhancements_section(c, main_deck, height_points):
    evil_enh = {k: v for k, v in main_deck.items() if v.get("type") == "EE"}
    place_section(c, evil_enh, 310, height_points - 892, line_spacing=16)


def place_artifacts_section(c, main_deck, height_points):
    artifacts = {
        k: v
        for k, v in main_deck.items()
        if v.get("type") in ["Artifact", "Covenant", "Curse"]
    }
    place_section(c, artifacts, 560, height_points - 178, line_spacing=16)


def place_fortresses_section(c, main_deck, height_points):
    fortresses = {
        k: v for k, v in main_deck.items() if v.get("type") in ["Fortress", "Site"]
    }
    place_section(c, fortresses, 560, height_points - 471, line_spacing=17)


def place_misc_section(c, main_deck, height_points):
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
    place_section(
        c, reserve, 580, height_points - 910, line_spacing=16, add_quantity=False
    )


def generate_decklist(deck_data):
    """
    Generate a deck check sheet overlay with card listings, section counts,
    and a total card count drawn separately. Section counts and the total are
    drawn independently so you can control their positions.
    """
    template_path = "data/pdfs/Type 1 Deck Check Sheet.pdf"
    output_path = "tbd/output_decklist.pdf"
    temp_overlay = "tbd/temp_overlay.pdf"

    reader = PdfReader(template_path)
    page = reader.pages[0]
    width_points = float(page.mediabox.width)
    height_points = float(page.mediabox.height)

    c = canvas.Canvas(temp_overlay, pagesize=(width_points, height_points))

    main_deck = deck_data.get("main_deck", {})
    reserve = deck_data.get("reserve", {})

    # Draw card listings
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

    # Draw section counts (just numbers, no labels)
    draw_count(
        c,
        {k: v for k, v in main_deck.items() if v.get("type") == "Dominant"},
        127,
        height_points - 150,
    )
    draw_count(
        c,
        {k: v for k, v in main_deck.items() if v.get("type") == "Hero"},
        95,
        height_points - 529,
    )
    draw_count(
        c,
        {k: v for k, v in main_deck.items() if v.get("type") == "GE"},
        191,
        height_points - 874,
    )
    draw_count(
        c,
        {k: v for k, v in main_deck.items() if v.get("type") == "Lost Soul"},
        383,
        height_points - 150,
    )
    draw_count(
        c,
        {k: v for k, v in main_deck.items() if v.get("type") == "Evil Character"},
        411,
        height_points - 529,
    )
    draw_count(
        c,
        {k: v for k, v in main_deck.items() if v.get("type") == "EE"},
        438,
        height_points - 874,
    )
    draw_count(
        c,
        {
            k: v
            for k, v in main_deck.items()
            if v.get("type") in ["Artifact", "Covenant", "Curse"]
        },
        743,
        height_points - 150,
    )
    draw_count(
        c,
        {k: v for k, v in main_deck.items() if v.get("type") in ["Fortress", "Site"]},
        710,
        height_points - 451,
    )
    draw_count(
        c,
        {
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
        },
        595,
        height_points - 685,
    )
    draw_count(c, reserve, 617, height_points - 872)

    # Draw total card count in the top right corner (separate box)
    box_width = 50
    box_height = 30
    top_margin = 40
    side_margin = 92
    c.rect(
        width_points - top_margin - box_width,
        height_points - side_margin - box_height,
        box_width,
        box_height,
    )
    # Total count in top right corner
    total_main = sum(int(card.get("quantity", 1)) for card in main_deck.values())
    c.setFont("Helvetica-Bold", 14)
    c.drawString(
        width_points - top_margin - box_width + 5,
        height_points - side_margin - box_height + 10,
        f"{total_main}",
    )

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
