@ -0,0 +1,416 @@
import argparse
import os

import dotenv
import PIL.Image as Image
import PIL.ImageDraw as ImageDraw
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from src.m_count.decklist import Decklist
from src.utilities.text_to_pdf import generate_decklist

dotenv.load_dotenv()
DECKLIST_FOLDER = "/Applications/LackeyCCG/plugins/Redemption/decks"
DECKLIST_IMAGES_FOLDER = (
    "/Applications/LackeyCCG/plugins/Redemption/sets/setimages/general/"
)
OUTPUT_IMAGES_FOLDER = "./deck_images"
OUTPUT_PDF_FOLDER = "tbd"

TINIFY_API_KEY = os.getenv("TINIFY_API_KEY")

# Create output folders if they don't exist
os.makedirs(OUTPUT_PDF_FOLDER, exist_ok=True)


def load_deck_data(decklist_file_path: str) -> dict:
    return Decklist(decklist_file_path).to_json()


def find_decklist_file(decklist_name: str) -> str:
    for file_name in os.listdir(DECKLIST_FOLDER):
        lower_decklist_name = decklist_name.lower()
        lower_file_name = file_name.lower()
        if lower_file_name.startswith(lower_decklist_name) and (
            file_name.endswith(".txt") or file_name.endswith(".dek")
        ):
            print(f"Found decklist file: {file_name}")
            return os.path.join(DECKLIST_FOLDER, file_name)
    raise FileNotFoundError(
        f"Decklist file starting with '{decklist_name}' not found in {DECKLIST_FOLDER}."
    )


def generate_image(
    deck_data: dict, deck_key: str, output_filename: str, cards_per_row: int = 10
):
    """Generate an image for the specified deck (either 'main_deck' or 'reserve')."""
    if cards_per_row == 0:
        cards_per_row = 10
    # Get the deck data
    deck = deck_data.get(deck_key, {})
    if not deck:
        print(f"No data found for '{deck_key}' deck.")
        return

    # Expand deck items by quantity
    expanded_deck_items = []
    for card_key, card_data in deck.items():
        for _ in range(card_data.get("quantity", 1)):
            expanded_deck_items.append((card_key, card_data))

    # Sort the deck by 'type' alphabetically
    sorted_deck_items = sorted(expanded_deck_items, key=lambda item: item[1]["type"])

    # Load the first card image to determine the size for consistent dimensions
    sample_image_path = os.path.join(
        DECKLIST_IMAGES_FOLDER,
        sorted_deck_items[0][1][
            "imagefile"
        ],  # Access the first card in the sorted deck
    )
    # Ensure the image has the correct extension
    if not sample_image_path.lower().endswith(".jpg"):
        sample_image_path += ".jpg"

    sample_image = Image.open(sample_image_path)
    card_width, card_height = sample_image.size

    # Set overlap amount to 10% of card height
    card_overlap = int(card_height * 0.10)

    # Calculate output image dimensions based on the number of cards, considering the overlap
    num_cards = len(expanded_deck_items)
    rows = (
        num_cards + cards_per_row - 1
    ) // cards_per_row  # Calculate required number of rows
    output_width = card_width * cards_per_row
    output_height = (card_height * rows) - (card_overlap * (rows - 1))

    # Create a blank canvas of the correct size with the new background color
    background_color = (30, 32, 43)  # RGB for #1e202b
    output_image = Image.new("RGB", (output_width, output_height), background_color)

    # Track positioning for placing card images on the canvas
    x_offset, y_offset = 0, 0

    for card_key, card_data in sorted_deck_items:
        image_file = card_data["imagefile"]
        # Ensure the image file has the correct extension
        if not image_file.lower().endswith(".jpg"):
            image_file += ".jpg"
        card_image_path = os.path.join(DECKLIST_IMAGES_FOLDER, image_file)

        try:
            card_image = Image.open(card_image_path)

            # Ensure the card image has the same mode as the output canvas
            if card_image.mode != output_image.mode:
                card_image = card_image.convert(output_image.mode)

            # Paste the card image directly without resizing to preserve quality
            output_image.paste(card_image, (x_offset, y_offset))

            # Update x_offset, and wrap to the next row if necessary
            x_offset += card_width
            if x_offset >= output_width:
                x_offset = 0
                y_offset += card_height - card_overlap
        except FileNotFoundError:
            print(
                f"Warning: Image for card '{card_key}' not found at {card_image_path}"
            )

    # Save the generated deck image as WebP
    output_image_path = os.path.join(OUTPUT_IMAGES_FOLDER, f"{output_filename}.webp")
    output_image.save(output_image_path, format="WEBP", quality=80, optimize=True)
    print(f"Deck image saved to {output_image_path}")


def combine_images(
    main_deck_image_path: str, reserve_deck_image_path: str, output_filename: str
):
    """
    Combine the main deck and reserve deck images into a single image,
    adding a line and padding between them.
    """

    # Load the main deck and reserve deck images
    main_deck_image = Image.open(main_deck_image_path)
    # check if the reserve deck image exists
    if not os.path.exists(reserve_deck_image_path):
        return
    reserve_deck_image = Image.open(reserve_deck_image_path)

    # Set line height for the red separator line
    line_height = 50

    # Set padding between main deck and reserve deck
    padding = 50  # You can adjust this value as needed

    # Calculate the combined image size
    combined_width = max(main_deck_image.width, reserve_deck_image.width)
    combined_height = (
        main_deck_image.height + reserve_deck_image.height + line_height + padding
    )

    # Create a blank canvas for the combined image with the new background color
    background_color = (30, 32, 43)  # RGB for #1e202b
    combined_image = Image.new(
        "RGB", (combined_width, combined_height), background_color
    )

    # Paste the main deck image at the top
    combined_image.paste(main_deck_image, (0, 0))

    # Draw a red line below the main deck image
    draw = ImageDraw.Draw(combined_image)
    line_color = (20, 22, 33)
    line_y_start = main_deck_image.height + (line_height // 2)
    draw.line(
        (0, line_y_start, combined_width, line_y_start),
        fill=line_color,
        width=line_height,
    )

    # Paste the reserve deck image below the line, with added padding
    reserve_y_offset = main_deck_image.height + line_height + padding
    combined_image.paste(reserve_deck_image, (0, reserve_y_offset))

    # Save the combined image using WebP optimization
    print("Saving combined image as WebP...")
    combined_image_path = os.path.join(
        OUTPUT_IMAGES_FOLDER, f"{output_filename}_optimized.webp"
    )
    combined_image.save(combined_image_path, format="WEBP", quality=80, optimize=True)

    file_size_mb = os.path.getsize(combined_image_path) / (1024 * 1024)
    print(f"Combined deck image saved to {combined_image_path}")
    print(f"File size: {file_size_mb:.2f}MB")


def find_decks(prefix: str):
    """Return all file names starting with the given prefix.

    Args:
        prefix (str): The prefix to search for in deck file names

    Returns:
        list: A list of file paths for decks matching the prefix
    """
    matching_decks = []
    for file_name in os.listdir(DECKLIST_FOLDER):
        if file_name.lower().startswith(prefix.lower()) and (
            file_name.endswith(".txt") or file_name.endswith(".dek")
        ):
            deck_path = os.path.join(DECKLIST_FOLDER, file_name)
            matching_decks.append(deck_path)

    if not matching_decks:
        print(f"No decks found with prefix '{prefix}'")
        return []

    print(f"Found {len(matching_decks)} deck(s) with prefix '{prefix}'")
    return matching_decks


def generate_deck_images(deck_type: str, deck_data, filename: str):
    # Extract base filename from path if it's a full path
    base_filename = (
        os.path.splitext(os.path.basename(filename))[0]
        if filename == "dynamic"
        else filename
    )

    main_deck_filename = f"{base_filename}_main"
    reserve_deck_filename = f"{base_filename}_reserve"
    if deck_type == "type_2":
        cards_per_row = 15
    else:
        cards_per_row = 10
    generate_image(
        deck_data,
        "reserve",
        reserve_deck_filename,
        cards_per_row=cards_per_row,
    )
    generate_image(
        deck_data,
        "main_deck",
        main_deck_filename,
        cards_per_row=cards_per_row,
    )

    main_deck_image_path = os.path.join(
        OUTPUT_IMAGES_FOLDER, f"{main_deck_filename}.webp"
    )
    reserve_deck_image_path = os.path.join(
        OUTPUT_IMAGES_FOLDER, f"{reserve_deck_filename}.webp"
    )
    combine_images(
        main_deck_image_path, reserve_deck_image_path, f"{base_filename}_combined"
    )

    # Delete the individual deck images after combining
    try:
        if os.path.exists(main_deck_image_path):
            os.remove(main_deck_image_path)
            print(f"Deleted main deck image: {main_deck_image_path}")
        if os.path.exists(reserve_deck_image_path):
            os.remove(reserve_deck_image_path)
            print(f"Deleted reserve deck image: {reserve_deck_image_path}")
    except OSError as e:
        print(f"Error deleting individual deck images: {e}")


def generate_text_decklist(deck_type: str, deck_data, filename: str) -> None:
    # generate_reserve_list(deck_data.get("reserve", {}))
    generate_decklist(deck_type, deck_data, filename=filename)


def generate_reserve_list(reserve_data):
    # Check reserve size
    total_cards = sum(
        card_info.get("quantity", 1) for card_info in reserve_data.values()
    )
    assert (
        total_cards <= 10
    ), f"Reserve list contains {total_cards} cards. Maximum allowed is 10."

    # Create a temporary file for the text overlay
    temp_overlay = os.path.join(OUTPUT_PDF_FOLDER, "temp_overlay.pdf")
    c = canvas.Canvas(temp_overlay, pagesize=(1137, 1469))  # Match template dimensions

    # Define grid layout parameters
    cols = 3
    rows = 4
    cell_width = 280  # Approximate width for each column
    cell_height = 246  # Approximate height for each row
    start_y = 968
    margin_left = 60  # Left margin for first column
    line_spacing = 16  # Space between lines

    # Sort card names once
    sorted_cards = sorted([(name, info) for name, info in reserve_data.items()])

    # Configure text settings
    c.setFont("Helvetica", 12)

    # Iterate through grid cells
    for row in range(rows):
        for col in range(cols):
            # Calculate position for current cell
            x = margin_left + (col * cell_width)
            y = start_y - (row * cell_height)

            # Reset font for card names
            c.setFont("Helvetica", 12)

            # Write card names for this cell
            current_y = y
            for card_name, card_info in sorted_cards:
                # text = f"{card_info.get('quantity', 1)}x {card_name}"
                text = f"{card_name}"
                c.drawString(x, current_y, text)
                current_y -= line_spacing

                # Break to next cell if we're getting too close to the next row
                if current_y < (y - cell_height + 40):
                    break

    c.save()

    # Combine with the template PDF
    template_path = "data/pdfs/Reserve List T1.pdf"
    output_path = os.path.join(OUTPUT_PDF_FOLDER, "output_reserve_list.pdf")

    # Merge the overlay with the template
    try:
        template_pdf = PdfReader(template_path)
        overlay_pdf = PdfReader(temp_overlay)

        output = PdfWriter()
        page = template_pdf.pages[0]
        page.merge_page(overlay_pdf.pages[0])
        output.add_page(page)

        with open(output_path, "wb") as output_file:
            output.write(output_file)

        print(f"Reserve list generated: {output_path}")
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
    finally:
        # Clean up temporary file
        if os.path.exists(temp_overlay):
            os.remove(temp_overlay)


def process_decklist(
    deck_type: str, mode: str, deck_name: str = None, prefix: str = None
):
    """Process deck list(s) based on either deck name or prefix.

    Args:
        deck_type (str): Type of deck ('type_1' or 'type_2')
        mode (str): Processing mode ('png' or 'pdf')
        deck_name (str, optional): Specific deck name to process
        prefix (str, optional): Prefix to match multiple decks
    """
    if not deck_name and not prefix:
        raise ValueError("Either deck_name or prefix must be provided")

    if prefix:
        decks = find_decks(prefix)
        for deck_path in decks:
            deck_data = load_deck_data(deck_path)
            filename = os.path.splitext(os.path.basename(deck_path))[0]
            if mode == "png":
                generate_deck_images(deck_type, deck_data, filename=filename)
            elif mode == "pdf":
                generate_text_decklist(deck_type, deck_data, filename=filename)
    else:
        decklist_file_path = find_decklist_file(deck_name)
        deck_data = load_deck_data(decklist_file_path)
        if mode == "png":
            generate_deck_images(deck_type, deck_data, filename=deck_name)
        elif mode == "pdf":
            generate_text_decklist(deck_type, deck_data, filename=deck_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process Redemption deck lists")
    parser.add_argument(
        "--deck-type",
        required=True,
        choices=["type_1", "type_2"],
        help="the type of deck (type_1 or type_2)",
    )
    parser.add_argument(
        "--deck-name",
        help="the name of a specific lackey deck file",
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=["png", "pdf"],
        help="output mode (png or pdf)",
    )
    parser.add_argument(
        "--prefix",
        help="prefix to match multiple deck names",
    )

    args = parser.parse_args()

    if not args.deck_name and not args.prefix:
        parser.error("Either --deck-name or --prefix must be provided")

    process_decklist(
        deck_type=args.deck_type,
        mode=args.mode,
        deck_name=args.deck_name,
        prefix=args.prefix,
    )