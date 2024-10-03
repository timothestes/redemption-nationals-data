# Primary Key: player_name

# columns we need to map
# Name	Set	ImageFile	OfficialSet	Type	Brigade	Strength	Toughness	Class	Identifier	SpecialAbility	Rarity	Reference	Sound	Alignment	Legality is_reserve

deck_schema = [
    "card_id",  # Primary key: unique identifier combining card_name and image_file
    "decklist_id",  # Foreign key: links the card to the decklist
    "player_name",  # The name of the player who owns the decklist
    "card_name",  # The name of the card
    "quantity",  # The quantity of this card in the deck
    "place",
    "image_file",  # Image file associated with the card
    "official_set",  # The official set of the card
    "type",  # The type of the card (e.g., Hero, Lost Soul, etc.)
    "brigade",  # The brigade of the card (color or faction)
    "n_brigades",  # Number of brigades associated with the card
    "strength",  # Strength of the card (if applicable)
    "toughness",  # Toughness of the card (if applicable)
    "class",  # Class of the card (e.g., Warrior)
    "identifier",  # Unique identifier of the card
    "special_ability",  # Any special ability text of the card
    "rarity",  # Rarity of the card
    "reference",  # Reference (scripture or source)
    "alignment",  # Alignment of the card (Good, Evil, etc.)
    "legality",  # Legality in tournament play
    "in_reserve",  # Boolean to check if the card is in the reserve
]
