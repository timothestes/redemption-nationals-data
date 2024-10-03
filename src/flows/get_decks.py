from prefect import flow, task


@task
def get_decklists() -> list:
    print("getting decklists")
    return ["1", "2"]


@task
def load_decklist(decklist):
    print("loading decklists")


@task
def write_deck_to_csv(deck):
    print("writing decklists")


@flow(log_prints=True)
def get_decks():

    decklists = get_decklists()
    for decklist in decklists:
        deck = load_decklist(decklist)
        write_deck_to_csv(deck)

    return


if __name__ == "__main__":
    # python3 -m src.flows.get_decks
    get_decks()
