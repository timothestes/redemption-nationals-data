import csv
import os
import random

from src.m_count.constants import (
    CYCLER_SOULS,
    DARKNESS,
    EVIL_BRIGADES,
    GOOD_BRIGADES,
    LAWLESS,
)
from src.m_count.decklist import Decklist
from src.m_count.models_v2 import Deck, Discard, Hand, Territory

MATTHEW_CSV_FILE = "src/m_count/matthew_game_log.csv"


class SpectrographSimulation:
    """Class contains all information necessary to run a spectrograph simulation."""

    def __init__(
        self,
        deck_file_path: str,
        n_simulations: int,
        cycler_logic: str,
        crowds_ineffectiveness_weight: float,
        matthew_fizzle_rate: float,
    ):
        self.deck_file_path = deck_file_path
        self.n_simulations = n_simulations
        self.cycler_logic = cycler_logic
        self.crowds_ineffectiveness_weight = crowds_ineffectiveness_weight
        self.matthew_fizzle_rate = matthew_fizzle_rate
        self.m_count = 0
        self.whiff_percentage = 0

    @staticmethod
    def create_empty_log_file():
        """Used to track information of games played."""
        headers = [
            "sim_number",
            "n_cards_matthew_drew",
            "deck_size",
            "cards_in_hand",
            "denarius_draw",
            "four_drachman_draw",
            "whiff_on_heroes",
        ]

        with open(MATTHEW_CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()

    def initialize_decklist(self):
        """Load the deck in."""
        self.decklist = self._load_raw_deck(self.deck_file_path)
        self.deck = Deck.load_decklist(self.decklist)
        self.territory = Territory(cards=[])
        self.discard = Discard(cards=[])
        self.hand = Hand(cards=[])
        # this makes it so that the simulation keeps 8 cards in hand.
        self._set_deck_flags(self.decklist)

    def _set_deck_flags(self, decklist: Decklist):
        """Set some flags that might be useful later."""
        self.going_first = True
        self.virgin_birth = False
        self.crowds = False
        self.denarius = False
        self.four_drachma = False
        for card in decklist.mapped_main_deck_list:
            if card == "Virgin Birth":
                self.virgin_birth = True
            elif card == 'Lost Soul "Crowds" [Luke 5:15] [2016 - Local]':
                self.crowds = True
            elif card == "Denarius (I/J+)":
                self.denarius = True
            elif card == "Four-Drachma Coin (GoC)":
                self.four_drachma = True

    @staticmethod
    def _load_raw_deck(deck_file_path: str) -> Decklist:
        """Read a txt file into a variable."""
        if not deck_file_path:
            raise AssertionError("Please provide a deck_file_path")

        if not os.path.isfile(deck_file_path):
            raise FileNotFoundError(f"No file found at {deck_file_path}")

        if not deck_file_path.endswith(".txt"):
            raise AssertionError("File must be a .txt file")

        return Decklist(deck_file_path)

    def _reset_simulation_state(self):
        """Reset the state of the simulation for a new run."""
        self.deck.reset(shuffle=True)
        self.territory.reset()
        self.discard.reset()
        self.hand.reset()

    def _draw_cards(self, n_cards: int, resolve_stars=False):
        """Handle anytime we draw cards during the game."""
        drawn_cards = self.deck.draw_n(n_cards)

        if resolve_stars:
            # resolve the virgin birth
            if self.virgin_birth:
                for i, card in enumerate(drawn_cards):
                    if card.name == "Virgin Birth":
                        # replace virgin birth with a card from the top 6
                        drawn_cards[i] = self.deck.resolve_the_virgin_birth(
                            drawn_cards[i],
                            self.cycler_logic,
                        )

        self.hand.add(drawn_cards)

        # handle lost souls that are in our hand
        while self.hand.count(type="Lost Soul") > 0:
            # put any lost souls in play
            lost_soul = self.hand.remove(type="Lost Soul")
            self.territory.add(lost_soul)
            # don't draw from empty deck
            if not self.deck.cards_in_deck == 0:
                # then redraw
                self.hand.add(self.deck.draw_n(1))

            if lost_soul.name in CYCLER_SOULS:
                self._resolve_cycler()
            elif lost_soul.name == 'Lost Soul "Prosperity" [Deuteronomy 30:15]':
                self._resolve_prosperity()
            elif lost_soul.name in DARKNESS:
                self._resolve_darkness()
            elif lost_soul.name in LAWLESS:
                self._resolve_lawless()

    def _resolve_darkness(self):
        """Randomly choose an evil character from deck and add it to hand"""
        # TODO: Logic currently cannot get dual-alignment evil characters
        evil_character = self.deck.search_for(type="Evil Character")
        if evil_character:
            self.hand.add(evil_character)

    def _resolve_prosperity(self):
        """Discard a card and draw 2 cards."""
        if self.cycler_logic == "optimized":
            self.discard.add(self.hand.remove(type="MostBrigades"))
        else:
            self.discard.add(self.hand.remove(type="RandomNonLostSoul"))
        self.hand.add(self.deck.draw_n(2))

    def _resolve_cycler(self):
        """Underdeck a random card and draw a card."""
        if self.cycler_logic == "optimized":
            self.deck.bottom_cards([self.hand.remove(type="MostBrigades")])
        else:
            self.deck.bottom_cards([self.hand.remove(type="RandomNonLostSoul")])

        self.hand.add(self.deck.draw_n(1))

    def _resolve_lawless(self):
        """Reveal top 6, put lost souls in play, and grab an evil card."""
        top_six = self.deck.draw_n(6)
        got_evil = False
        for i, card in enumerate(top_six):
            if card.type == "Lost Soul":
                self.territory.add(top_six.pop(i))
                if card.name in CYCLER_SOULS:
                    self._resolve_cycler()
            elif not got_evil and card.alignment == "Evil":
                # TODO: Logic can't currently grab three woes or other "evil" neutral cards...
                self.hand.add(top_six.pop(i))
                got_evil = True
        # underdeck the rest
        self.deck.bottom_cards(top_six)

    def _calculate_matthew_count(self, sim_number) -> dict:
        """Actions to take when when Matthew inevitably attacks."""
        if random.random() < self.matthew_fizzle_rate:
            # matthew deck fizzled
            n_brigades_in_hand = 0
        # crowds lost soul logic
        elif (
            self.crowds
            # if we drew crowds
            and self.territory.count(
                name='Lost Soul "Crowds" [Luke 5:15] [2016 - Local]'
            )
            > 0
            # factor in the times matthew decks will have an answer
            and random.random() > self.crowds_ineffectiveness_weight
        ):
            # we have hand protection. 0 brigades drawn with Matthew
            n_brigades_in_hand = 0
        else:
            n_brigades_in_hand = self._count_n_brigades_in_hand()
        return {
            "sim_number": sim_number,
            "n_cards_matthew_draw": n_brigades_in_hand,
            "deck_size": self.decklist.deck_size,
        }

    def _play_denarius(self, denarius_from_deck=False):
        """Play Denarius, search for an Emperor, then draw 3 cards."""
        self.artifact_slot_used_for_turn = True
        source = self.deck if denarius_from_deck else self.hand
        self.territory.add(source.remove(name="Denarius (I/J+)"))

        emperor = self.deck.search_for(tags="is_emperor") or self.hand.search_for(
            tags="is_emperor"
        )
        if emperor:
            self.territory.add(emperor)

        if self.territory.search_for(tags="is_emperor"):
            self.output["denarius_draw"] = True
            self._draw_cards(n_cards=3, resolve_stars=False)

    def _play_peter_and_coin(self, coin_from_deck=False):
        """Play Simon Peter and 4 Drachma Coin, then draw 4 cards."""
        source = self.deck if coin_from_deck else self.hand
        self.territory.add(source.remove(name="Four-Drachma Coin (GoC)"))
        self.territory.add(self.hand.remove(name="Simon Peter / Peter, the Rock (GoC)"))
        self.output["four_drachman_draw"] = True
        self._draw_cards(n_cards=4)

    def _play_delivered(self):
        """Try to use Delivered to get 4-drachma coin or Denarius out."""
        if (
            self.four_drachma
            and not self.output["four_drachman_draw"]
            and self.hand.count(name="Simon Peter / Peter, the Rock (GoC)") > 0
            and self.deck.count(name="Four-Drachma Coin (GoC)") > 0
        ):
            self.discard.add(self.hand.remove(name="Delivered"))
            self._play_peter_and_coin(coin_from_deck=True)
        elif (
            self.denarius
            and not self.output["denarius_draw"]
            and self.deck.count(name="Denarius (I/J+)") > 0
        ):
            self.discard.add(self.hand.remove(name="Delivered"))
            self._play_denarius(denarius_from_deck=True)

    def _take_solitaire_turn(self) -> dict:
        """Take a turn, trying to 'combo' off"""
        self.territory_class_for_turn = False
        self.artifact_slot_used_for_turn = False
        self.output = {
            "cards_in_hand": None,
            "denarius_draw": False,
            "four_drachman_draw": False,
            "whiff_on_heroes": False,
        }

        def check_and_play():
            if (
                self.hand.count(name="Denarius (I/J+)") > 0
                and not self.artifact_slot_used_for_turn
            ):
                self._play_denarius()
            if (
                self.hand.count(name="Four-Drachma Coin (GoC)") > 0
                and self.hand.count(name="Simon Peter / Peter, the Rock (GoC)") > 0
            ):
                self._play_peter_and_coin()
            if (
                self.hand.count(name="Delivered")
                and not self.territory_class_for_turn
                and (
                    self.hand._search_for_brigades(
                        brigades=["Teal", "Green", "Evil Gold", "Pale Green"]
                    )
                    or self.territory._search_for_brigades(
                        brigades=["Teal", "Green", "Evil Gold", "Pale Green"]
                    )
                )
            ):
                self._play_delivered()

        # Initial check to play cards
        check_and_play()

        # After initial draw, check again
        if self.output["denarius_draw"] or self.output["four_drachman_draw"]:
            check_and_play()

        # Check for 0 heroes
        if self.hand.count(type="Hero") == 0 and self.territory.count(type="Hero") == 0:
            self.output["whiff_on_heroes"] = True

        return self.output

    def _count_n_brigades_in_hand(self) -> int:
        """
        Count the number of unique brigades in hand, handling 'multi' brigade specially.
        """
        brigades = set()
        for card in self.hand.cards:
            brigades.update(card.brigade)

        return len(brigades)

    @staticmethod
    def append_log_to_file(log_data: list[dict], csv_file: str):
        """Bulk add rows of log data to the CSV file."""
        with open(csv_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=log_data[0].keys())
            writer.writerows(log_data)

    def run(self, **kwargs):
        """Simulate N games of Redemption by drawing 8 cards from a deck."""
        all_logs = []  # Collect all logs to write in bulk
        for sim_number in range(self.n_simulations):
            self._reset_simulation_state()  # Reset deck, hand, discard, and territory

            # draw 8 cards from deck
            self._draw_cards(n_cards=8, resolve_stars=True)

            # count n_brigades from matthew
            turn_log = self._calculate_matthew_count(sim_number)

            if "only_matthew_results" not in kwargs:
                # take a solitaire turn
                additional_information = self._take_solitaire_turn()
                turn_log.update(additional_information)

            # Collect logs
            all_logs.append(turn_log)

        # # Bulk write logs at the end of all simulations
        self.append_log_to_file(all_logs, MATTHEW_CSV_FILE)

    def print_results(self) -> tuple[float, float]:
        """Print the summary statistics of the simulation."""
        matthew_column_sum = 0
        total_rows = 0
        denarius_count = 0
        four_drachma_count = 0
        whiff_count = 0

        with open(MATTHEW_CSV_FILE, "r") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                try:
                    matthew_column_sum += float(row["n_cards_matthew_drew"])
                    denarius_count += 1 if row["denarius_draw"] == "True" else 0
                    four_drachma_count += (
                        1 if row["four_drachman_draw"] == "True" else 0
                    )
                    whiff_count += 1 if row["whiff_on_heroes"] == "True" else 0
                    total_rows += 1
                except (ValueError, KeyError) as e:
                    print(e)
                    continue  # Handle non-numeric values or missing keys

        if total_rows > 0:
            average_matthew_drew = matthew_column_sum / total_rows
            self.m_count = average_matthew_drew
            denarius_percentage = (denarius_count / total_rows) * 100
            four_drachma_percentage = (four_drachma_count / total_rows) * 100
            whiff_percentage = (whiff_count / total_rows) * 100
            self.whiff_percentage = whiff_percentage

            # print(f"Average number of cards Matthew drew: {average_matthew_drew:.2f}")
            # print(f"Percentage of Denarius draws: {denarius_percentage:.2f}%")
            # print(f"Percentage of Four-Drachma draws: {four_drachma_percentage:.2f}%")
            # print(f"Percentage of whiffs on heroes: {whiff_percentage:.2f}%")
        else:
            print("No valid data found")
