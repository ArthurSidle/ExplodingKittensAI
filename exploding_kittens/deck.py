import random
from structs import *

class Deck:
    def __init__(self):
        composition = {
            CardTypes.EXPLODING_KITTEN: 4,
            CardTypes.DEFUSE: 6,
            CardTypes.ATTACK: 4,
            CardTypes.FAVOR: 4,
            CardTypes.NOPE: 5,
            CardTypes.SHUFFLE: 4,
            CardTypes.SKIP: 4,
            CardTypes.SEE_THE_FUTURE: 5,
            CardTypes.RAINBOW_CAT: 4,
            CardTypes.POTATO_CAT: 4,
            CardTypes.TACOCAT: 4,
            CardTypes.CATTERMELON: 4,
            CardTypes.BEARD_CAT: 4
        }

        self._cards = []
        for card_type in CardTypes:
            card_set = [Card(card_type)] * composition[card_type]
            self._cards.extend(card_set)

        #print(self._cards)


    def shuffle(self):
        random.shuffle(self._cards)


    # Returns a function that acts as a filter on a set of cards
    def card_fn(self, key=None, exclude=None, include=None):
        null = object()

        def fn(value):
            if key:
                value = getattr(value, key, null)
            return (
                (exclude and value in exclude)
                or (include and value not in include)
            )
        return fn


    # Returns and removes the first card from the deck that meets the requirements of the filter
    def get_card(self, fn=None):
        if fn is None:
            fn = lambda card: False

        card = None
        cards = []
        while card is None:
            # Note: if self._cards is empty an IndexError will be thrown
            card = self._cards.pop()
            if fn(card):
                cards.append(card)
                card = None
        self._cards.extend(reversed(cards))
        return card


    def get_cards(self, n, fn=None):
        return tuple(self.get_card(fn=fn) for _ in range(n))
    

    def get_deck(self):
        return self._cards
    

    def is_empty(self):
        return len(self._cards) == 0
    

    def see_the_future(self):
        three_cards = self._cards[-3::1].copy()
        three_cards.reverse()
        return three_cards
    
    def add_kitten(self):
        self._cards.insert(random.randrange(0, len(self._cards)), Card(CardTypes.EXPLODING_KITTEN))