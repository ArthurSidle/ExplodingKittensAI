import random

from structs import *
from collections import Counter


class Player:
    def __init__(self, id, type, game):
        self.id = id
        self.type = type
        self.__game = game
        self.__hand = []
        self.turns_left = 1
    

    # Adds a card to the hand
    def add_card(self, card):
        self.__hand.append(card)
        return card
    

    # Removes a card of the specified type to the hand and returns the removed card
    def remove_card(self, card_type, amount=1):
        removed_cards = []

        for card in self.__hand:
            if card is not None:
                if card.type == card_type:
                    removed_cards.append(card)
                    self.__hand.remove(card)
                    amount -= 1
                    if amount == 0:
                        return removed_cards[0]

        if removed_cards:
            return removed_cards[0]
        else:
            return None
    

    def draw_card(self):
        return self.add_card(self.__game.deck.get_card())


    def draw_safe_card(self):
        fn = self.__game.deck.card_fn('type', exclude={CardTypes.EXPLODING_KITTEN})
        self.add_card(self.__game.deck.get_card(fn))


    def draw_defuse_card(self):
        fn = self.__game.deck.card_fn('type', include={CardTypes.DEFUSE})
        self.add_card(self.__game.deck.get_card(fn))
    

    def draw_initial_cards(self):
        for i in range(0, 7):
            self.draw_safe_card()


    def has_card(self, card_type):
        for card in self.__hand:
            if card.type == card_type:
                return True
        return False


    # Returns the set of actions the player can perform as commands
    def get_commands(self, full=False):
        command_list = ActionList()

        # adds draw action if the deck is not empty
        if self.__game.deck.is_empty() == False: 
            command_list.add_command(Action(self, MoveTypes.DRAW))

        # sets up dictionary that counts occurences of cards' types in hand
        card_types_in_hand = [card.type for card in self.__hand]
        card_types_counter = Counter(card_types_in_hand)

        for card_type in card_types_counter.items():
            a = card_type[0].value.name
            # if the card's type has an action associated with it then add it to the list of actions
            if card_type[0].value.move_type is not None:
                if card_type[0].value.move_type == MoveTypes.FAVOR:
                    for player in self.__game.get_other_players():
                        command_list.add_command(Action(self, card_type[0].value.move_type, requested_player=player))
                else:
                    command_list.add_command(Action(self, card_type[0].value.move_type))
            
            # if there is more than 1 of a card make 2 of a kind available
            if card_type[1] > 1:
                if full:
                    for player in self.__game.get_other_players():
                        command_list.add_command(Action(self, MoveTypes.TWO_OF_A_KIND, card_type[0], player))
                else:
                    command_list.add_command(Action(self, MoveTypes.TWO_OF_A_KIND, card_type[0]))
            
            # if there is more than 2 of a card make 3 of a kind available
            if card_type[1] > 2:
                if full:
                    for player in self.__game.get_other_players():
                        for card_type_2 in CardTypes.get_playable_types():
                            command_list.add_command(Action(self, MoveTypes.TWO_OF_A_KIND, card_type[0], player, card_type_2))
                else:
                    command_list.add_command(Action(self, MoveTypes.THREE_OF_A_KIND, card_type[0]))
        
        return command_list


    def get_favor_commands(self):
        commands = ActionList()

        # sets up dictionary that counts occurences of cards in hand
        card_counter = Counter(self.__hand)

        for card in card_counter.items():
            commands.add_command(Action(self, given_card=card[0].type))
        
        return commands
    


    def get_hand(self):
        return self.__hand
    

    def get_hand_names(self):
        return [card.get_name() for card in self.__hand]


    def get_random_card_type_from_hand(self):
        card_index = random.randint(0, len(self.__hand) - 1)
        card = self.__hand[card_index]
        return card.type


    def give_card(self, player, card_type):
        player.add_card(self.remove_card(card_type))
    

    def steal_chosen_card(self):
        card = None
        options = self.__hand.copy()
        options.append('Play NOPE')

        if self.type == PlayerTypes.HUMAN:
            valid = False
            while valid == False:
                print(options)
                card = input(self.watermark('Select a card to give (or play NOPE): '))

                if card.lower() == 'play nope':
                    return None
                elif card in options:

                    valid = True
                else:
                    print('Error: Please enter a valid player.')
        
        return card