# Foreign Key: player_name
# Primary Key:

# other columns (but lowercase them and put underscores in them if multiple words)
# Name	Set	ImageFile	OfficialSet	Type	Brigade	Strength	Toughness	Class	Identifier	SpecialAbility	Rarity	Reference	Sound	Alignment	Legality is_reserve

schema = {
    "player_name": "str",  # PK, FK
    "name": "str",
    "set": "str",
    "image_file": "str",
    "official_set": "str",
    "type": "str",
    "brigade": "str",
    "n_brigades": "int",
    "strength": "int",
    "toughness": "int",
    "class": "str",
    "identifier": "str",
    "special_ability": "str",
    "rarity": "str",
    "reference": "str",
    "alignment": "str",
    "legality": "str",
    "is_reserve": "bool",
}
