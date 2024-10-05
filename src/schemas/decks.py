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

metadata_tags = {
    "1": {"offense": "nativity", "defense": "herods"},
    "2": {"offense": "nativity", "defense": "herods"},
    "3": {"offense": "nativity", "defense": "thieves"},
    "4": {"offense": "clay", "defense": "herods"},
    "5": {"offense": "clay", "defense": "herods"},
    "6": {"offense": "clay", "defense": "black/gray"},
    "7": {"offense": "clay", "defense": "herods"},
    "8": {"offense": "daniel", "defense": "demons"},
    "9": {"offense": "clay", "defense": "thieves"},
    "10": {"offense": "priests", "defense": "black"},
    "11": {"offense": "nativity", "defense": "black/gray"},
    "12": {"offense": "nativity", "defense": "black/gray"},
    "13": {"offense": "daniel", "defense": "demons"},
    "14": {"offense": "blue", "defense": "pale green"},
    "15": {"offense": "clay", "defense": "thieves"},
    "16": {"offense": "clay", "defense": "black soul hide"},
    "17": {"offense": "nativity", "defense": "thieves"},
    "18": {"offense": "clay", "defense": "herods"},
    "19": {"offense": "blue", "defense": "black/gray"},
    "20": {"offense": "clay", "defense": "herods"},
    "21": {"offense": "clay", "defense": "herods"},
    "22": {"offense": "clay", "defense": "herods"},
    "23": {"offense": "red", "defense": "black soul hide"},
    "24": {"offense": "clay", "defense": "black/gray soul hide"},
    "25": {"offense": "clay", "defense": "herods"},
    "26": {"offense": "clay", "defense": "herods"},
    "27": {"offense": "priests", "defense": "babylonians"},
    "28": {"offense": "blue", "defense": "pale green"},
    "29": {"offense": "clay", "defense": "herods"},
    "30": {"offense": "music leader", "defense": "black soul hide"},
    "31": {"offense": "clay", "defense": "misc"},
    "32": {"offense": "clay", "defense": "herods"},
    "33": {"offense": "silver", "defense": "demons"},
    "34": {"offense": "wilderness", "defense": "herods"},
    "35": {"offense": "purple", "defense": "black"},
    "36": {"offense": "clay", "defense": "herods"},
    "37": {"offense": "clay", "defense": "herods"},
    "38": {"offense": "silver", "defense": "gray"},
    "39": {"offense": "ruth", "defense": "gray"},
    "40": {"offense": "gold", "defense": "herods"},
    "41": {"offense": "nativity", "defense": "gray"},
    "42": {"offense": "flood", "defense": "black soul hide"},
    "43": {"offense": "gold", "defense": "herods"},
    "44": {"offense": "music leader", "defense": "black"},
    "45": {"offense": "nativity", "defense": "black soul hide"},
    "46": {"offense": "misc", "defense": "misc"},
    "47": {"offense": "gold", "defense": "thieves"},
    "48": {"offense": "music leader", "defense": "thieves"},
    "49": {"offense": "musicians", "defense": "misc"},
    "50": {"offense": "prophets", "defense": "demons"},
    "51": {"offense": "gold", "defense": "pale green"},
    "52": {"offense": "clay", "defense": "black"},
    "53": {"offense": "honeypot", "defense": "gray"},
    "54": {"offense": "clay", "defense": "herods"},
    "55": {"offense": "clay", "defense": "herods"},
    "56": {"offense": "music leader", "defense": "gray"},
    "57": {"offense": "misc", "defense": "demons"},
    "58": {"offense": "blue", "defense": "pale green"},
}
