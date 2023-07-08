# Adapted from https://stackcodereview.com/simulate-a-simplified-version-of-exploding-kittens-in-python/
import random
import collections
import enum

Card = collections.namedtuple('Card', 'type')
Player = collections.namedtuple('Player', 'id hand')


class CardTypes(enum.Enum):
    EXPLODING_KITTEN = 'Exploding Kitten'
    REGULAR = 'Regular'


class Deck:
    def __init__(self, kittens=4, regulars=48):
        self._cards = [
            Card(i) for i in (
                [CardTypes.EXPLODING_KITTEN] * kittens
                + [CardTypes.REGULAR] * regulars
            )
        ]

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

    # Returns the card on top of the deck unless it meets the requirements of the filter
    def get_card(self, fn=None):
        if fn is None:
            fn = lambda card: False

        card = None
        cards = []
        while card is None:
            card = self._cards.pop()
            if fn(card):
                cards.append(card)
                card = None
        self._cards.extend(reversed(cards))
        return card

    def get_cards(self, n, fn=None):
        return tuple(self.get_card(fn=fn) for _ in range(n))


class ExplodingKittens:
    def __init__(self, amount_players):
        self._deck, self._players = self.start_game(amount_players)

    def start_game(self, amount_players):
        deck = Deck(amount_players - 1, 53 - amount_players)
        deck.shuffle()
        exclude_kittens = deck.card_fn('type', exclude={CardTypes.EXPLODING_KITTEN})
        players = [
            Player(f'Player {id + 1}', list(deck.get_cards(4, exclude_kittens)))
            for id in range(amount_players)
        ]
        deck.shuffle()
        return deck, players

    def play_round(self):
        index = 0
        while index < len(self._players):
            player = self._players[index]
            card = self._deck.get_card()
            player.hand.append(card)
            print('{} drew {}'.format(player.id, card.type.value))

            if card.type is CardTypes.EXPLODING_KITTEN:
                print('{} is dead!'.format(player.id))
                self._players.pop(index)
            else:
                index += 1

            if len(self._players) == 1:
                print('{} won the game!'.format(self._players[0].id))
                return

    def decide_winner(self):
        while len(self._players) > 1:
            self.play_round()


if __name__ == "__main__":
    game = ExplodingKittens(5)
    print(game._players)
    game.decide_winner()