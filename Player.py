import sys

class Player():
    def __init__(self, lives, name):
        self.hand = []
        self.lives = lives
        self.name = name
    
    def __repr__(self):
        ret_str = ""
        ret_str += "Hand: " + str(self.hand) + "\n"
        ret_str += "Lives: " + str(self.lives) + "\n"
        return ret_str

    def reset(self):
        self.hand = []

    def count_hand(self):
        running_count = 0
        if self.hand:
            for card in self.hand:
                temp_count = 0
                if card.value == 14: # Ace
                    temp_count = 11
                elif card.value >= 10:
                    temp_count = 10
                else:
                    temp_count = card.value
                running_count += temp_count

        return running_count

    def play_card(self, player_action, card_value):
        pass