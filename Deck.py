import os
from enum import Enum
from datetime import datetime
from random import shuffle, seed

SUIT_ENUM = {}


class Suit(Enum):
    H = 1
    D = 2
    C = 3
    S = 4

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False


class Card():
    def __init__(self, suit, value):
        if suit and value:
            self.suit = suit
            self.set_value(value)
        else:
            print "Check Suit and Value"

    def __eq__(self, other):
        return (self.suit == other.suit) and (self.value == other.value)

    def __repr__(self):
        p_value = ""
        if self.value == 11:
            p_value = "J"
        elif self.value == 12:
            p_value = "Q"
        elif self.value == 13:
            p_value = "K"
        elif self.value == 14:
            p_value = "A"
        else:
            p_value = str(self.value)

        return "%s%s" % (p_value, self.suit)

    def set_value(self, value):
        if RepresentsInt(value):
            if (int(value) > 0) and (int(value) < 15):
                self.value = int(value)

        elif isinstance(value, str):
            if value == "J":
                self.value = 11
            if value == "Q":
                self.value = 12
            if value == "K":
                self.value = 13
            if value == "A":
                self.value = 14      

    def get_card_score(self):
        ret_value = 0

        if self.value <= 10:
            ret_value = self.value
        elif self.value == 14:
            ret_value = 11
        else:
            ret_value = 10

        return ret_value


class Deck():
    def __init__(self):
        self.cards = []
        seed(datetime.now())

        for i in range(1,5):
            for j in range(2,15):
                suit = Suit(i).name
                value = j
                self.cards.append(Card(suit, value))

    def __repr__(self):
        return str(self.cards)

    def __len__(self):
        return len(self.cards)

    def shuffle(self):
        shuffle(self.cards)


def main():
    d = Deck()
    print d.cards
    d.shuffle()
    print d.cards

if __name__ == '__main__':
    main()
