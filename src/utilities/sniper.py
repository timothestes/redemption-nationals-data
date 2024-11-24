import os

import PIL.Image as Image

from src.m_count.decklist import Decklist

DECKLIST_FOLDER = "/Applications/LackeyCCG/plugins/Redemption/decks"
DECKLIST_IMAGES_FOLDER = (
    "/Applications/LackeyCCG/plugins/Redemption/sets/setimages/general/"
)
OUTPUT_IMAGES_FOLDER = "./deck_images"
MAIN_DECK_LENGTH = 600
MAIN_DECK_WIDTH = 600
RESERVE_LENGTH = 900
RESERVE_WIDTH = 200


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
    # Create a blank canvas
    output_image = Image.new("RGB", (RESERVE_LENGTH, RESERVE_WIDTH), (255, 255, 255))

    # Calculate dimensions for each card image to fit within the output image
    card_width = RESERVE_WIDTH // 5
    card_height = RESERVE_LENGTH // 5

    # Track positioning for placing card images on the canvas
    x_offset, y_offset = 0, 0

    for card, card_data in deck_data["reserve"].items():
        image_file = card_data["imagefile"]
        if not image_file.lower().endswith(".jpg"):
            image_file += ".jpg"
        card_image_path = os.path.join(DECKLIST_IMAGES_FOLDER, image_file)
        try:
            card_image = Image.open(card_image_path).resize((card_width, card_height))
            output_image.paste(card_image, (x_offset, y_offset))

            # Update x_offset, and move to next row if necessary
            x_offset += card_width
            if x_offset >= RESERVE_WIDTH:
                x_offset = 0
                y_offset += card_height
        except FileNotFoundError:
            print(
                f"Warning: Image for card '{card['name']}' not found at {card_image_path}"
            )

    # Save the generated deck image
    output_image_path = os.path.join(OUTPUT_IMAGES_FOLDER, "deck_image.jpg")
    output_image.save(output_image_path)
    print(f"Deck image saved to {output_image_path}")


def process_decklist():
    decklist_name = input("Enter the decklist name: ").strip()
    decklist_file_path = find_decklist_file(decklist_name)
    deck_data = load_deck_data(decklist_file_path)
    generate_image(deck_data)


if __name__ == "__main__":
    process_decklist()
