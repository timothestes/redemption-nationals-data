deck_schema = [
    "card_id",  # Primary key: image_file
    "decklist_id",  # Foreign key: decklist file name
    "place",  # The place (1st, 2nd, etc.) derived from decklist file
    "player_name",  # The name of the player who owns the decklist
    "quantity",  # The quantity of this card in the deck
    "brigade",  # The brigade of the card (color or faction)
    "n_brigades",  # Number of brigades associated with the card
    "card_name",  # The name of the card
    "in_reserve",  # Boolean to check if the card is in the reserve
    "image_file",  # Image file associated with the card
    "official_set",  # The official set of the card
    "type",  # The type of the card (e.g., Hero, Lost Soul, etc.)
    "strength",  # Strength of the card (if applicable)
    "toughness",  # Toughness of the card (if applicable)
    "class",  # Class of the card (e.g., Warrior)
    "identifier",  # Unique identifier of the card
    "special_ability",  # Any special ability text of the card
    "rarity",  # Rarity of the card
    "reference",  # Reference (scripture or source)
    "alignment",  # Alignment of the card (Good, Evil, etc.)
    "legality",  # Legality in tournament play
]
