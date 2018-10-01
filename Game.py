import sys
import logging
from collections import OrderedDict

from Player import Player
from Deck import Deck, Card, Suit
from DB import DBInterfacer


MISTAKE_VALUE = 3
HAND_SIZE = 4
NUM_PLAYERS = 2

class Game():
    def __init__(self, num_players=2, lives=3):
        logging.basicConfig(filename='crazy.log', level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

        self.db = DBInterfacer()
        self.db.create_table("GameEvents", OrderedDict([("action", "STRING"), ("player", "STRING"), ("game", "INTEGER"), ("round", "INTEGER"),
            ("cardname", "STRING"), ("cardvalue", "INTEGER")]))
        self.db.create_table("GameAudit", OrderedDict([("game", "INTEGER"), ("numplayers", "INTEGER")]))

        self.dealer = 0
        self.current_player = 0

        self.round = 0
        self.winner = 0  # 1 when game has been won
        self.game_state = 1  # 1 for dead, 0 for alive
        self.chained_cards = 0

        self.play_direction = 1
        self.current_suit = 0

        self.starting_lives = lives
        self.players = []

        for i in range(num_players):
            self.players.append(Player(lives=self.starting_lives, number=i+1))

        self.played_cards = []

    def start_new_game(self, num_players=2):
        self.dealer = 0
        self.current_player = 0

        self.round = 0
        self.winner = 0

        self.players = []
        for i in range(num_players):
            self.players.append(Player(lives=self.starting_lives, number=i+1))

        # Retrieve the last game's number and increment
        last_game_number = self.db.retrieve("GameAudit", ["game"], 1)
        if last_game_number == []:
            self.game_num = 1
        else:
            self.game_num = int(last_game_number[0][0]) + 1

        self.db.insert("GameAudit", {"game": self.game_num, "numplayers": len([player for player in self.players if (player.lives > 0)])})

        return True

    def start_new_round(self, hand_size):
        for player in self.players:
            player.reset_hand()

        self.game_state = 0
        self.round += 1

        self.dealer = self.current_player = (self.dealer + 1) % len(self.players)

        self.played_cards = []

        self.deck = Deck()
        self.deck.shuffle()
        self.deal(hand_size)

        return True

    def deal(self, hand_size):
        rotation_num = (self.round - 1) % len(self.players)
        rotated_player_list = self.players[rotation_num:] + self.players[:rotation_num]

        self.logger.debug("Rotated player list: {0}".format(str(rotated_player_list)))

        for i in range(hand_size):
            for player in rotated_player_list:
                top_card = self.deck.cards.pop(0)
                player.hand.append(top_card)
                self.db.insert("GameEvents", {"action": "DEAL", "player": player.number, "game": self.game_num,
                                              "round": self.round, "cardname": repr(top_card), "cardvalue": top_card.get_card_score()})

        # Flip first card
        first_card = self.deck.cards.pop(0)
        self.played_cards.append(first_card)
        self.validate_card(first_card)
        self.set_current_suit(first_card.suit)

        return True

    def get_players(self):
        return self.players

    def get_current_player(self):
        return self.players[self.current_player]

    def count_hands(self):
        scores = [player.count_hand() for player in self.players]

        self.logger.debug("Hand scores: {0}".format([(player.get_name(), player_score) for player, player_score in zip(self.players, scores)]))

        return scores

    def calculate_loser(self):
        scores = self.count_hands()
        max_score = max(scores)
        losers = [i for i, j in enumerate(scores) if j == max_score]

        for loser in losers:
            self.players[loser].lives -= 1

        losing_players = [self.players[loser] for loser in losers]
        self.logger.debug("{0} lost lives.".format(str([player.get_name() for player in losing_players])))

        return losing_players

    def pick_up_card(self, num_cards=1):
        if self.chained_cards:
            last_card = self.played_cards[-1]
            if last_card.value == 7:
                multiplier = 1
            elif last_card.value == 2:
                multiplier = 2
            num_cards = self.chained_cards * multiplier
            self.chained_cards = 0

        if len(self.deck) == 0:
            self.deck.cards = self.played_cards[1:]
            self.played_cards = [self.played_cards[0]]

        for i in range(num_cards):
            top_card = self.deck.cards.pop(0)
            self.get_current_player().hand.append(top_card)
            self.db.insert("GameEvents", {"action": "PICK", "player": self.get_current_player().number, "game": self.game_num, 
                "round": self.round, "cardname": repr(top_card), "cardvalue": top_card.get_card_score()})

        print "PICKED UP {0} CARDS".format(num_cards)
        self.current_player = (self.current_player + 1) % len(self.players)

        return True

    def end_game(self):
        print "Game over. Player {0} won!".format(self.get_current_player().get_name())

        losers = self.calculate_loser()
        for loser in losers:
            print "{0} lost. Now has {1} lives.".format(loser.get_name(), loser.lives)

        self.players = [player for player in self.players if player.lives > 0]
        if len(self.players) == 1:
            self.winner = 1

        self.logger.debug("Player Lives: {0}".format([(player.get_name(), player.lives) for player in self.players]))

        self.game_state = 1

        return True

    def set_current_suit(self, suit=None):
        if not suit:
            print_str =  "1. Hearts | 2. Diamonds | 3. Clubs | 4. Spades"
            in_card = int(raw_input(print_str))
            self.current_suit = Suit(in_card).name
        else:
            self.current_suit = suit

    def validate_card(self, card):
        last_card = self.played_cards[-1]

        if self.chained_cards > 0:
            if card.value != last_card.value:
                if last_card.value == 7:
                    multiplier = 1
                elif last_card.value == 2:
                    multiplier = 2

                pickup_num = ((self.chained_cards * multiplier) + MISTAKE_VALUE)
                
                self.chained_cards = 0
                print "MISTAKE! Pick up {0} cards..".format(pickup_num)
                return (False, pickup_num)
            else:
                self.chained_cards += 1
                self.set_current_suit(card.suit)
                return (True, 0)

        if card.value == 14:  # Ace
            if len(self.get_current_player().hand) == 1:
                print "MISTAKE! Pick up {0} cards.!".format(MISTAKE_VALUE)
                return (False, MISTAKE_VALUE)
            else:
                self.set_current_suit()
                return (True, 0)

        if card.value != last_card.value and card.suit != self.current_suit:
            print "{0} == {1}, {2} == {3}".format(card.value, last_card.value, card.suit, last_card.suit)
            print "MISTAKE! Pick up {0} cards..".format(MISTAKE_VALUE)
            return (False, MISTAKE_VALUE)
        else:
            if card.value == 7:
                self.chained_cards += 1
            if card.value == 2:
                self.chained_cards += 1
            if card.value == 11:
                self.play_direction *= -1
            self.set_current_suit(card.suit)
            return (True, 0)

    def play_card(self, in_card):
        player_card = self.get_current_player().hand[in_card]
        print "Played {0}".format(player_card)

        validation, num_cards = self.validate_card(player_card)

        # If a mistake is made, pick up cards
        if validation is False:
            self.pick_up_card(num_cards=num_cards)
            return False
        else:
            self.get_current_player().hand.pop(in_card)
            self.played_cards.append(player_card)

            self.db.insert("GameEvents", {"action": "PLAY", "player": self.get_current_player().number, "game": self.game_num, "round": self.round, 
                "cardname": repr(player_card), "cardvalue": player_card.get_card_score()})

            if len(self.get_current_player().hand) == 0:
                self.end_game()
            else:
                if player_card.value == 8:
                    self.current_player = (self.current_player + 2) % len(self.players)
                elif player_card.value == 11 and len([player for player in self.players if player.lives > 0]) == 2:
                    self.current_player = self.current_player
                else:
                    self.current_player = (self.current_player + self.play_direction) % len(self.players)

            return True


def main():

    g = Game()

    while True:
        g.start_new_game(num_players=NUM_PLAYERS)
        print g.players
        while g.winner == 0:
            g.start_new_round(hand_size=HAND_SIZE)
            print "Starting round {0}".format(g.round)
            while g.game_state == 0:
                current_player = g.get_current_player()
                print "{0} hand: {1}".format(current_player.get_name(), current_player.hand)
                print "Last card: {0}".format(g.played_cards[-1])
                try:
                    print_str = " | ".join(["{0}. {1}".format(idx+1, card) for idx, card in enumerate(g.get_current_player().hand)])
                    print_str += " | {0}. {1}\n".format(str(len(g.get_current_player().hand) + 1), "Pick Up")
                    in_card = int(raw_input(print_str)) - 1 # Minus 1 as we start selections at 1

                    if in_card == len(g.get_current_player().hand):
                        g.pick_up_card()
                    elif in_card < len(g.get_current_player().hand) and in_card >= 0:
                        g.play_card(in_card)
                    else:
                        print "Invalid input!"
                except ValueError as e:
                    print e

        print "WINNER WINNER CHICKEN DINNER!"

        print "Press 'a' to play again!"

        try:
            in_str = str(raw_input('Input: '))
            if in_str == "a":
                g.start_new_game(hand_size=HAND_SIZE)
            else:
                break
        except ValueError as e:
            print e


if __name__ == '__main__':
    main()
