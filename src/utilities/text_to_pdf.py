import os
import re

from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

# Precompile regex patterns for efficiency.
SET_NAME_PATTERN = re.compile(r"(\([^)]*\))\s*$")
LOST_SOUL_PREFIX_PATTERN = re.compile(r"^Lost Soul\s+")
BRACKET_PATTERN = re.compile(r"\[([^\]]+)\]")
HYPHEN_PATTERN = re.compile(r"\s*-\s*[^]]+")


def clean_card_name(card_name, card_data):
    """
    Clean the card name.
    - If the name contains a '/', use the part before it and append any trailing set name in parentheses.
    - For Lost Soul cards, remove the "Lost Soul " prefix and any hyphenated text inside brackets.
    """
    if "/" in card_name:
        base_name = card_name.split("/")[0].strip()
        match = SET_NAME_PATTERN.search(card_name)
        if match:
            return f"{base_name} {match.group(1).strip()}"
        return base_name

    if card_data.get("type") == "Lost Soul" and card_name.startswith("Lost Soul"):
        display_name = LOST_SOUL_PREFIX_PATTERN.sub("", card_name)

        def bracket_repl(match):
            inner = match.group(1)
            inner_clean = HYPHEN_PATTERN.sub("", inner)
            return f"[{inner_clean.strip()}]"

        display_name = BRACKET_PATTERN.sub(bracket_repl, display_name)
        first_bracket = BRACKET_PATTERN.search(display_name)
        if first_bracket:
            display_name = display_name[: first_bracket.end()].strip()
        return display_name

    return card_name


def place_section(c, section_data, x, y, line_spacing, add_quantity=True):
    """
    Place sorted items from section_data at (x, y) on the canvas.
    """
    for card_name, card_data in sorted(section_data.items(), key=lambda item: item[0]):
        display_name = clean_card_name(card_name, card_data)
        display_text = (
            f"{card_data.get('quantity', 1)}x {display_name}"
            if add_quantity
            else display_name
        )
        c.drawString(x, y, display_text)
        y -= line_spacing


def draw_count(c, section_data, x, y, font="Helvetica", font_size=12):
    """
    Draw just the total count (number) for section_data at (x, y).
    """
    total = sum(int(card.get("quantity", 1)) for card in section_data.values())
    c.setFont(font, font_size)
    c.drawString(x, y, str(total))


def place_section_by_type(
    c, main_deck, card_types, x, y, line_spacing, add_quantity=True
):
    """
    Filter main_deck by card_types and place the section.
    """
    if isinstance(card_types, str):
        filtered = {k: v for k, v in main_deck.items() if v.get("type") == card_types}
    else:
        filtered = {k: v for k, v in main_deck.items() if v.get("type") in card_types}
    place_section(c, filtered, x, y, line_spacing, add_quantity)


def generate_decklist(deck_data):
    """
    Generate a deck check sheet overlay with card listings, section counts,
    and a total card count drawn separately. Section counts and the total
    are drawn independently so you have full control over their positions.
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
    place_section_by_type(c, main_deck, "Dominant", 57, height_points - 177, 16)
    place_section_by_type(c, main_deck, "Hero", 57, height_points - 545, 16)
    place_section_by_type(c, main_deck, "GE", 54, height_points - 892, 16)
    place_section_by_type(c, main_deck, "Lost Soul", 310, height_points - 177, 16)
    place_section_by_type(c, main_deck, "Evil Character", 310, height_points - 545, 16)
    place_section_by_type(c, main_deck, "EE", 310, height_points - 892, 16)
    place_section_by_type(
        c, main_deck, ["Artifact", "Covenant", "Curse"], 560, height_points - 178, 16
    )
    place_section_by_type(
        c, main_deck, ["Fortress", "Site"], 560, height_points - 471, 17
    )
    # Misc section (cards not fitting other types)
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
    place_section(c, misc, 560, height_points - 709, 17)
    # Reserve section (without quantity)
    place_section(c, reserve, 580, height_points - 910, 16, add_quantity=False)

    # Draw section counts (numbers only; positions are fully controlled)
    draw_count(
        c,
        {k: v for k, v in main_deck.items() if v.get("type") == "Dominant"},
        125,
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
        188,
        height_points - 874,
    )
    draw_count(
        c,
        {k: v for k, v in main_deck.items() if v.get("type") == "Lost Soul"},
        381,
        height_points - 150,
    )
    draw_count(
        c,
        {k: v for k, v in main_deck.items() if v.get("type") == "Evil Character"},
        408,
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
        742,
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

    # Draw total card count in the top right corner
    box_width = 50
    box_height = 30
    top_margin = 40
    side_margin = 92
    total_main = sum(int(card.get("quantity", 1)) for card in main_deck.values())
    c.setFont("Helvetica-Bold", 18)  # Changed from 14 to 18
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
