import os

import PIL.Image as Image
import PIL.ImageDraw as ImageDraw

from src.m_count.decklist import Decklist

DECKLIST_FOLDER = "/Applications/LackeyCCG/plugins/Redemption/decks"
DECKLIST_IMAGES_FOLDER = (
    "/Applications/LackeyCCG/plugins/Redemption/sets/setimages/general/"
)
OUTPUT_IMAGES_FOLDER = "./deck_images"


def load_deck_data(decklist_file_path: str) -> dict:
    return Decklist(decklist_file_path).to_json()


def find_decklist_file(decklist_name: str) -> str:
    for file_name in os.listdir(DECKLIST_FOLDER):
        if file_name.startswith(decklist_name) and file_name.endswith(".txt"):
            return os.path.join(DECKLIST_FOLDER, file_name)
    raise FileNotFoundError(
        f"Decklist file starting with '{decklist_name}' not found in {DECKLIST_FOLDER}."
    )


def generate_image(
    deck_data: dict, deck_key: str, output_filename: str, cards_per_row: int = 10
):
    """Generate an image for the specified deck (either 'main_deck' or 'reserve')."""

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

    # Save the generated deck image in a high-quality, lossless PNG format
    output_image_path = os.path.join(OUTPUT_IMAGES_FOLDER, f"{output_filename}.png")
    output_image.save(output_image_path, dpi=(300, 300), optimize=True)
    print(f"Deck image saved to {output_image_path}")


def combine_images(
    main_deck_image_path: str, reserve_deck_image_path: str, output_filename: str
):
    """Combine the main deck and reserve deck images into a single image, adding a line and padding between them."""

    # Load the main deck and reserve deck images
    main_deck_image = Image.open(main_deck_image_path)
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

    # Save the combined image in a high-quality, lossless PNG format
    combined_image_path = os.path.join(OUTPUT_IMAGES_FOLDER, f"{output_filename}.png")
    combined_image.save(combined_image_path, dpi=(300, 300), optimize=True)
    print(f"Combined deck image saved to {combined_image_path}")


def process_decklist():
    decklist_name = input("Enter the decklist name: ").strip()
    decklist_file_path = find_decklist_file(decklist_name)
    deck_data = load_deck_data(decklist_file_path)

    # Generate images for both the reserve and main decks
    main_deck_filename = "main_deck"
    reserve_deck_filename = "reserve"
    generate_image(
        deck_data,
        "reserve",
        reserve_deck_filename,
        cards_per_row=len(deck_data["reserve"]),
    )
    generate_image(deck_data, "main_deck", main_deck_filename, cards_per_row=10)

    # Combine the main deck and reserve deck images into one
    main_deck_image_path = os.path.join(
        OUTPUT_IMAGES_FOLDER, f"{main_deck_filename}.png"
    )
    reserve_deck_image_path = os.path.join(
        OUTPUT_IMAGES_FOLDER, f"{reserve_deck_filename}.png"
    )
    combine_images(main_deck_image_path, reserve_deck_image_path, "combined_deck")


if __name__ == "__main__":
    process_decklist()
