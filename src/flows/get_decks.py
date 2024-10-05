import os

from prefect import flow, task

from src.utilities.tools import (
    get_decklist_id,
    get_decklists,
    get_place,
    get_player_name,
)


@task
def write_deck_to_csv(decklist_path):
    decklist_id = get_decklist_id(decklist_path)
    player_name = get_player_name(decklist_id)
    place = get_place(decklist_id)


@flow(log_prints=True)
def get_decks():
    decklists = get_decklists()
    append = False

    for decklist_path in decklists:
        write_deck_to_csv(decklist_path)


if __name__ == "__main__":
    get_decks()
