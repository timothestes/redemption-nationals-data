import csv
import json

import pandas as pd
from prefect import flow, task

from src.schemas.decks import metadata_tags
from src.utilities.tools import (
    get_decklist_id,
    get_decklists,
    get_place,
    get_player_name,
)


def get_offense(place: int) -> str:
    if str(place) not in metadata_tags:
        raise KeyError(f"Could not find {place} in metadata tags!")
    return metadata_tags[str(place)]["offense"]


def get_defense(place: int) -> str:
    if str(place) not in metadata_tags:
        raise KeyError(f"Could not find {place} in metadata tags!")
    return metadata_tags[str(place)]["defense"]


def get_players_offense(player_name: str) -> str:
    if player_name == "bye":
        return None
    decklists = get_decklists()
    place = None
    for decklist in decklists:
        if player_name in decklist:
            place = get_place(decklist)

    if not place:
        # who's zach hill?
        return None
        raise ValueError(f"Could not find {player_name} in decklists!")

    return get_offense(place)


def get_players_defense(player_name: str) -> str:
    if player_name == "bye":
        return None
    decklists = get_decklists()
    place = None
    for decklist in decklists:
        if player_name in decklist:
            place = get_place(decklist)

    if not place:
        # who's zach hill?
        return None
        raise ValueError(f"Could not find {player_name} in decklists!")

    return get_defense(place)


@task
def get_pairings(pairings_data_path="data/pairings/nats2024_T12P_swiss.csv") -> dict:
    pairings_data = {}
    # Read CSV while skipping the first header row
    df = pd.read_csv(pairings_data_path, skiprows=1)

    # Loop through each row (player)
    for i, row in df.iterrows():
        player_name: str = row["Player Name"]
        player_name = player_name.lower().replace(" ", "_")
        player_data = {
            "total_points": row["Total points"],
            "total_ls_differential": row["Total LS Differential"],
            "overall_rank": row["Overall Rank"],
            "rounds": {},
        }

        # Iterate through the rounds dynamically
        for round_num in range(1, 8):
            player_data["rounds"][f"round_{round_num}"] = {
                "opponent_name": (
                    row[f"Opponent Name.{round_num - 1}"]
                    if round_num > 1
                    else row["Opponent Name"]
                ),
                "round_score": (
                    row[f"Round Score.{round_num - 1}"]
                    if round_num > 1
                    else row["Round Score"]
                ),
                "ls_differential": (
                    row[f"Round LS Differential.{round_num - 1}"]
                    if round_num > 1
                    else row["Round LS Differential"]
                ),
                "player_score": (
                    row[f"Player Score.{round_num - 1}"]
                    if round_num > 1
                    else row["Player Score"]
                ),
                "opponent_score": (
                    row[f"Opponent Score.{round_num - 1}"]
                    if round_num > 1
                    else row["Opponent Score"]
                ),
            }
            if (
                type(player_data["rounds"][f"round_{round_num}"]["opponent_name"])
                is str
            ):
                player_data["rounds"][f"round_{round_num}"]["opponent_name"] = (
                    player_data["rounds"][f"round_{round_num}"]["opponent_name"]
                    .lower()
                    .replace(" ", "_")
                )

        pairings_data[player_name] = player_data

    # Write to a JSON file
    with open("data/pairings/pairings.json", "w") as json_file:
        json.dump(pairings_data, json_file, indent=4)

    return pairings_data


def get_deck_field_names() -> list[str]:
    return [
        "decklist_id",
        "player_name",
        "place",
        "offense",
        "defense",
        "total_points",
        "total_ls_differential",
        "rank",
    ] + [
        f"round_{n}_{attr}"
        for n in range(1, 8)
        for attr in [
            "opponent",
            "score",
            "ls_differential",
            "player_score",
            "opponent_score",
            "opponent_offense",
            "opponent_defense",
        ]
    ]


@task
def write_deck_to_csv(pairings, decklist_path, append):
    decklist_id = get_decklist_id(decklist_path)
    player_name = get_player_name(decklist_id)
    place = get_place(decklist_id)
    offense = get_offense(place)
    defense = get_defense(place)
    # m_count = get_mcount(decklist_id)
    # n_cards_in_deck = get_n_cards_in_deck(decklist_id)
    output_path = "data/tables/decks.csv"
    mode = "a" if append else "w"

    with open(output_path, mode, newline="") as csvfile:
        # Define the common fields and the round-specific fields
        fieldnames = get_deck_field_names()

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not append:
            writer.writeheader()

        if player_name not in pairings:
            raise AssertionError(f"{player_name} not found in pairings!")

        # Extract player data from pairings
        player_data = pairings[player_name]
        rounds = player_data["rounds"]
        print(player_name)
        row = {
            "decklist_id": decklist_id,
            "player_name": player_name,
            "place": place,
            "offense": offense,
            "defense": defense,
            "total_points": player_data["total_points"],
            "total_ls_differential": player_data["total_ls_differential"],
        }

        # Add round data dynamically
        for n in range(1, 8):
            round_data = rounds[f"round_{n}"]
            row[f"round_{n}_opponent"] = round_data["opponent_name"]
            row[f"round_{n}_score"] = round_data["round_score"]
            row[f"round_{n}_ls_differential"] = round_data["ls_differential"]
            row[f"round_{n}_player_score"] = round_data["player_score"]
            row[f"round_{n}_opponent_score"] = round_data["opponent_score"]
            row[f"round_{n}_opponent_offense"] = get_players_offense(
                round_data["opponent_name"]
            )
            row[f"round_{n}_opponent_defense"] = get_players_defense(
                round_data["opponent_name"]
            )

        writer.writerow(row)


@flow(log_prints=True)
def get_decks():
    decklists = get_decklists()
    pairings = get_pairings()
    append = False

    for decklist_path in decklists:
        write_deck_to_csv(pairings, decklist_path, append)
        append = True


if __name__ == "__main__":
    get_decks()
