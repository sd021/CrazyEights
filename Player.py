import sys

class Player():
    def __init__(self, lives, name):
        self.hand = []
        self.lives = lives
        self.name = name
    
    def __repr__(self):
        ret_str = ""
        ret_str += "{0}".format(self.name)
        ret_str += "Hand: " + str(self.hand) + "\n"
        ret_str += "Lives: " + str(self.lives) + "\n"
        return ret_str

    def __getitem__(self):
        return self

    def reset_hand(self):
        self.hand = []

    def count_hand(self):
        running_count = 0
        if self.hand:
            for card in self.hand:
                running_count += card.get_card_score()

        return running_count

