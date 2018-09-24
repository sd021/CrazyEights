import sys

class Player():
    def __init__(self, lives, number):
        self.hand = []
        self.lives = lives
        self.number = number

    def __repr__(self):
        ret_str = ""
        ret_str += "{0}".format(self.get_name())
        ret_str += "Hand: " + str(self.hand) + "\n"
        ret_str += "Lives: " + str(self.lives) + "\n"
        return ret_str

    def reset_hand(self):
        self.hand = []

    def get_name(self):
        return "Player {0}".format(self.number)

    def count_hand(self):
        running_count = 0
        if self.hand:
            for card in self.hand:
                running_count += card.get_card_score()

        return running_count
