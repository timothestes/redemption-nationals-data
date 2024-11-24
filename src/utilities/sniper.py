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


def generate_image(deck_data: dict):
    """Generate an image of the specified dimensions for the deck."""

    # Get the number of cards in the reserve
    num_cards = len(deck_data["reserve"])

    # Load the first card image to determine the size for consistent dimensions
    sample_image_path = os.path.join(
        DECKLIST_IMAGES_FOLDER,
        deck_data["reserve"][list(deck_data["reserve"].keys())[0]]["imagefile"],
    )
    # Ensure the image has the correct extension
    if not sample_image_path.lower().endswith(".jpg"):
        sample_image_path += ".jpg"

    sample_image = Image.open(sample_image_path)
    card_width, card_height = sample_image.size

    # Calculate output image dimensions based on the number of cards
    output_width = card_width * num_cards
    output_height = card_height

    # Create a blank canvas of the correct size
    output_image = Image.new("RGB", (output_width, output_height), (255, 255, 255))

    # Track positioning for placing card images on the canvas
    x_offset = 0

    for card, card_data in deck_data["reserve"].items():
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
            output_image.paste(card_image, (x_offset, 0))

            # Update x_offset for the next card
            x_offset += card_width
        except FileNotFoundError:
            print(f"Warning: Image for card '{card}' not found at {card_image_path}")

    # Save the generated deck image in a high-quality, lossless PNG format
    output_image_path = os.path.join(OUTPUT_IMAGES_FOLDER, "deck_image.png")
    output_image.save(output_image_path, dpi=(300, 300), optimize=True)
    print(f"Deck image saved to {output_image_path}")


def process_decklist():
    decklist_name = input("Enter the decklist name: ").strip()
    decklist_file_path = find_decklist_file(decklist_name)
    deck_data = load_deck_data(decklist_file_path)
    generate_image(deck_data)


if __name__ == "__main__":
    process_decklist()
