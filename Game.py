import sys
from Player import Player
from Deck import Deck, Card
from DB import DBInterfacer
import logging

class Game():
    def __init__(self, players=2, lives=3):
        logging.basicConfig(filename='crazy.log', level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

        self.db = DBInterfacer()
        self.db.create_table("GameEvents", {"game": "INTEGER", "action": "STRING" ,"round": "INTEGER", "cardname": "STRING", "cardvalue": "INTEGER"})
        self.db.create_table("GameAudit", {"game": "INTEGER", "numplayers": "INTEGER"})

        self.dealer = 0
        self.current_player = 0

        self.round = 0
        self.winner = 0  # 1 when game has been won
        self.game_state = 1  # 1 for dead, 0 for alive

        self.starting_lives = lives
        self.players = []

        for i in range(players):
            self.players.append(Player(lives=self.starting_lives, name="Player {0}".format(i+1)))

        self.played_cards = []

    def start_new_game(self):
        self.dealer = 0
        self.current_player = 0

        self.round = 0
        self.winner = 0

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

        self.deck = Deck()
        self.deck.shuffle()

        self.played_cards = []
        self.deal(hand_size)

        self.dealer = (self.dealer + 1) % len(self.players)
        self.current_player = self.dealer

        self.game_state = 0
        self.round += 1

        return True

    def deal(self, hand_size):
        def list_rotator(l, n): return l[n:] + l[:n]

        rotated_player_list = list_rotator(self.players, 1)
        for i in range(hand_size):
            for player in rotated_player_list:
                player.hand.append(self.deck.cards.pop(0))
        return True

    def get_players(self):
        return self.players

    def get_current_player(self):
        return self.players[self.current_player]

    def count_hands(self):
        scores = [player.count_hand() for player in self.players]

        self.logger.debug("Hand scores: {0}".format([(player.name, player_score) for player, player_score in zip(self.players, scores)]))

        return scores

    def calculate_loser(self):
        scores = self.count_hands()
        max_score = max(scores)
        losers = [i for i, j in enumerate(scores) if j == max_score]

        for loser in losers:
            self.players[loser].lives -= 1

        losing_players = [self.players[loser] for loser in losers]
        self.logger.debug("{0} lost lives.".format(str([player.name for player in losing_players])))

        return losing_players

    def pick_up_card(self, num_cards=1):
        for i in range(num_cards):
            self.get_current_player().hand.append(self.deck.cards.pop(0))

        return True

    def end_game(self):
        print "Game over. Player {0} won!".format(self.get_current_player().name)

        losers = self.calculate_loser()
        for loser in losers:
            print "{0} lost. Now has {1} lives.".format(loser.name, loser.lives)

        self.players = [player for player in self.players if player.lives > 0]
        if len(self.players) = 1:
            self.winner = 1

        self.logger.debug("Player Lives: {0}".format([(player.name, player.lives) for player in self.players]))

        self.game_state = 1

        return True

    def play_card(self, card):
        print "Played {0}".format(card)
        if card in repr(self.players[self.current_player].hand):
            # Create card object from input
            card_obj = Card(card[-1], card[:-1])

            hand_idx = self.get_current_player().hand.index(card_obj)
            player_card = self.get_current_player().hand.pop(hand_idx)

            self.played_cards.append(player_card)

            self.db.insert("GameEvents", {"action": "PLAY", "game": self.game_num, "round": self.round, "cardname": repr(player_card), "cardvalue": player_card.get_card_score()})
            
            if len(self.get_current_player().hand) == 0:
                self.end_game()
            else:
                self.current_player = (self.current_player + 1) % len(self.players)

            return True
        else:
            return False


def main():
    HAND_SIZE = 1
    g = Game()

    while True:
        g.start_new_game()
        print g.players
        while g.winner == 0:
            g.start_new_round(hand_size=HAND_SIZE)
            print "Starting round {0}".format(g.round)
            while g.game_state == 0:
                current_player = g.get_current_player()
                print "It's {0}'s go.".format(str(current_player.name))
                print "{0} hand: ".format(current_player.name)
                print current_player.hand
                print "Last card"
                print g.played_cards[-1:]
                try:
                    in_card = str(raw_input('Card: '))

                    g.play_card(in_card)
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
