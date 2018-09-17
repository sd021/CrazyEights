import sys
from Player import Player
from Deck import *

class Game():
    def __init__(self, players=2, lives=3):
        self.players = []
        self.starting_lives = lives
        for i in range(players):
            self.players.append(Player(lives=self.starting_lives, name="Player {0}".format(i+1)))


        self.deck = Deck()
        self.deck.shuffle()

        self.dealer = 0
        self.current_player = 0

        self.round = 0
        self.winner = 0  # 1 when game has been won
        self.game_state = 1 # 1 for dead, 0 for alive

        self.played_cards = []

    def start_game(self, hand_size):
        for player in self.players:
            player.hand = []

        self.deal(hand_size)
        self.dealer = (self.dealer + 1) % len(self.players)
        self.current_player = self.dealer
        self.game_state = 0
        self.winner = 0
        self.round += 1
        return True



    def deal(self, hand_size):
        for i in range(hand_size):
            for player in self.players:
                player.hand.append(self.deck.cards.pop(0))        
        return True

    def get_players(self):
        return self.players

    def get_current_player(self):
        return self.players[self.current_player]

    def count_hands(self):
        ret_list = []
        for player in self.players:
            score = player.count_hand()
            ret_list.append(score)

        return ret_list
    
    def calculate_loser(self):
        scores = self.count_hands()
        max_score = max(scores)
        losers = [i for i, j in enumerate(scores) if j == max_score]
        for loser in losers:
            self.players[loser].lives -= 1
        
        return [self.players[loser] for loser in losers]

    def end_game(self):
       
        print "Ending the game."

        losers = self.calculate_loser()
        print "Game over. Player {0} won!".format(self.get_current_player().name)
        for loser in losers:
            print "{0} lost. Now has {1} lives.".format(loser.name, loser.lives)

        for idx, player in enumerate(self.players):
            if player.lives == 0:
                self.winner = 1
                self.round = 1
            print "{0} lives: {1}".format(player.name, player.lives)

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

            if len(self.get_current_player().hand) == 0:
                self.end_game()
            else:
                self.current_player = (self.current_player + 1) % len(self.players)

        return True



def main():
    HAND_SIZE = 1
  
    while True:
        g = Game()
        print g.players
        while g.winner == 0:
            g.start_game(hand_size=HAND_SIZE)
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
            in_str = str(raw_input('Input:'))
            if in_str == "a":
                g.start_game(hand_size=HAND_SIZE)
            else:
                break
        except ValueError as e:
            print e
        

if __name__ == '__main__':
    main()
