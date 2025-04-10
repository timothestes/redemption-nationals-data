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
    - For Lost Soul cards:
        - Keep quoted nicknames (without quotes)
        - Keep first verse reference only
        - Remove set information in brackets
    """
    # Special handling for Lost Souls
    if card_data.get("type") == "Lost Soul" and "Lost Soul" in card_name:
        nickname_match = re.search(r'"([^"]+)"', card_name)
        if nickname_match:
            nickname = nickname_match.group(1)  # group(1) gets content without quotes
            verse_match = re.search(r"\[([^/\]]+)", card_name)
            if verse_match:
                verse = f"[{verse_match.group(1)}]"
                return f"{nickname} {verse}"
        return card_name.split("[")[0].strip()

    # Handle cards with set information, special case for (I/J+)
    if "/" in card_name and "(I/J+)" not in card_name:
        base_name = card_name.split("/")[0].strip()
        match = SET_NAME_PATTERN.search(card_name)
        if match:
            return f"{base_name} {match.group(1).strip()}"
        return base_name

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
    place_section_by_type(c, main_deck, "Dominant", 57, height_points - 180, 16)
    place_section_by_type(c, main_deck, "Hero", 57, height_points - 548, 16)
    place_section_by_type(c, main_deck, "GE", 57, height_points - 895, 16)
    place_section_by_type(c, main_deck, "Lost Soul", 310, height_points - 180, 16)
    place_section_by_type(c, main_deck, "Evil Character", 310, height_points - 548, 16)
    place_section_by_type(c, main_deck, "EE", 310, height_points - 895, 16)
    place_section_by_type(
        c, main_deck, ["Artifact", "Covenant", "Curse"], 560, height_points - 181, 16
    )
    place_section_by_type(
        c, main_deck, ["Fortress", "Site", "City"], 560, height_points - 474, 16
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
            "City",
        ]
    }
    place_section(c, misc, 560, height_points - 700, 16)
    # Reserve section (without quantity)
    place_section(c, reserve, 580, height_points - 913, 16, add_quantity=False)

    # Draw section counts (numbers only; positions are fully controlled)
    draw_count(
        c,
        {k: v for k, v in main_deck.items() if v.get("type") == "Dominant"},
        124,
        height_points - 153,
    )
    draw_count(
        c,
        {k: v for k, v in main_deck.items() if v.get("type") == "Hero"},
        97,
        height_points - 532,
    )
    draw_count(
        c,
        {k: v for k, v in main_deck.items() if v.get("type") == "GE"},
        189,
        height_points - 877,
    )
    draw_count(
        c,
        {k: v for k, v in main_deck.items() if v.get("type") == "Lost Soul"},
        381,
        height_points - 154,
    )
    draw_count(
        c,
        {k: v for k, v in main_deck.items() if v.get("type") == "Evil Character"},
        408,
        height_points - 532,
    )
    draw_count(
        c,
        {k: v for k, v in main_deck.items() if v.get("type") == "EE"},
        439,
        height_points - 877,
    )
    draw_count(
        c,
        {
            k: v
            for k, v in main_deck.items()
            if v.get("type") in ["Artifact", "Covenant", "Curse"]
        },
        741,
        height_points - 153,
    )
    draw_count(
        c,
        {
            k: v
            for k, v in main_deck.items()
            if v.get("type") in ["Fortress", "Site", "City"]
        },
        710,
        height_points - 454,
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
                "City",
            ]
        },
        596,
        height_points - 687,
    )
    draw_count(c, reserve, 617, height_points - 875)

    # Draw total card count in the top right corner
    box_width = 50
    box_height = 30
    right_margin = 41
    top_margin = 97
    total_main = sum(int(card.get("quantity", 1)) for card in main_deck.values())
    c.setFont("Helvetica-Bold", 18)  # Changed from 14 to 18
    c.drawString(
        width_points - right_margin - box_width + 5,
        height_points - top_margin - box_height + 10,
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
