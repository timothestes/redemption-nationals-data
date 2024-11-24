import os

import PIL.Image as Image

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

    # Load the first card image to determine the size for consistent dimensions
    sample_image_path = os.path.join(
        DECKLIST_IMAGES_FOLDER,
        deck[list(deck.keys())[0]]["imagefile"],
    )
    # Ensure the image has the correct extension
    if not sample_image_path.lower().endswith(".jpg"):
        sample_image_path += ".jpg"

    sample_image = Image.open(sample_image_path)
    card_width, card_height = sample_image.size

    # Calculate output image dimensions based on the number of cards
    num_cards = len(deck)
    rows = (
        num_cards + cards_per_row - 1
    ) // cards_per_row  # Calculate the required number of rows
    output_width = card_width * cards_per_row
    output_height = card_height * rows

    # Create a blank canvas of the correct size
    output_image = Image.new("RGB", (output_width, output_height), (255, 255, 255))

    # Track positioning for placing card images on the canvas
    x_offset, y_offset = 0, 0

    for card, card_data in deck.items():
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
                y_offset += card_height
        except FileNotFoundError:
            print(f"Warning: Image for card '{card}' not found at {card_image_path}")

    # Save the generated deck image in a high-quality, lossless PNG format
    output_image_path = os.path.join(OUTPUT_IMAGES_FOLDER, f"{output_filename}.png")
    output_image.save(output_image_path, dpi=(300, 300), optimize=True)
    print(f"Deck image saved to {output_image_path}")


def process_decklist():
    decklist_name = input("Enter the decklist name: ").strip()
    decklist_file_path = find_decklist_file(decklist_name)
    deck_data = load_deck_data(decklist_file_path)

    # Generate images for both the reserve and main decks
    generate_image(
        deck_data, "reserve", "reserve", cards_per_row=len(deck_data["reserve"])
    )
    generate_image(deck_data, "main_deck", "main_deck", cards_per_row=10)


if __name__ == "__main__":
    process_decklist()
