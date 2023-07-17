# Adapted from https://codereview.stackexchange.com/questions/196533/simulate-a-simplified-version-of-exploding-kittens-in-python
import random
import cmd
import random

from collections import Counter

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
            if card.type == card_type:
                removed_cards.append(card)
                self.__hand.remove(card)
                amount -= 1
                if amount == 0:
                    return removed_cards[0]

        return removed_cards[0]
    

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


    def has_defuse(self):
        for card in self.__hand:
            if card.type == CardTypes.DEFUSE:
                return True
        return False
    

    # Returns the set of actions the player can perform as commands
    def get_commands(self):
        command_list = CommandList()

        # adds draw action if the deck is not empty
        if self.__game.deck.is_empty() == False: 
            command_list.add_command(Command(MoveTypes.DRAW))

        # sets up dictionary that counts occurences of cards' types in hand
        card_types_in_hand = [card.type for card in self.__hand]
        card_types_counter = Counter(card_types_in_hand)

        for card_type in card_types_counter.items():
            a = card_type[0].value.name
            # if the card's type has an action associated with it then add it to the list of actions
            if card_type[0].value.move_type is not None:
                command_list.add_command(Command(card_type[0].value.move_type))
            
            # if there is more than 1 of a card make 2 of a kind available
            if card_type[1] > 1:
                command_list.add_command(Command(MoveTypes.TWO_OF_A_KIND, card_type[0]))
            
            # if there is more than 2 of a card make 3 of a kind available
            if card_type[1] > 2:
                command_list.add_command(Command(MoveTypes.THREE_OF_A_KIND, card_type[0]))
        
        return command_list
    

    def get_favor_actions(self):
        actions = []

        # sets up dictionary that counts occurences of cards in hand
        card_counter = Counter(self.__hand)

        for card in card_counter.items():
            actions.append(card.type)
        
        return actions


    def get_hand(self):
        return self.__hand
    

    def get_hand_names(self):
        return [card.get_name() for card in self.__hand]


    def get_random_card_type_from_hand(self):
        card_index = random.randint(0, len(self.__hand))
        card = self.__hand[card_index]
        return card.type


    def give_card(self, player, card_type):
        player.add_card(self.remove_card(card_type))


    def get_move_input(self):
        move = None
        if self.type == PlayerTypes.HUMAN:
            valid = False
            while valid == False:
                self.__game.out(f'Hand: {self.__hand}')
                move = input(self.watermark('Enter a move: '))
                try:
                    move = MoveTypes(move.lower())
                    valid = True
                except KeyError:
                    self.__game.out('Error: Please enter a valid move.')

        return move
    

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
    
    
    

class ExplodingKittens(cmd.Cmd):
    def __init__(self, player_types):
        super().__init__(self)
        self.phase = GamePhases.MAIN
        self.deck, self.players = self.start_game(player_types)
        self.current_player = 0

        self.chosen_player = None
        self.turns = 0
        self.favor_actions = None
        self.combo_card_type = None


    def start_game(self, player_types):
        deck = Deck()
        deck.shuffle()
        players = [
            Player(f'Player {i + 1}', player_types[i], self)
            for i in range(len(player_types))
        ]
        return deck, players


    def start_of_phase(self):
        self.command_list = self.get_current_player().get_commands()
        self.prompt = f'({self.get_current_player().id}) '
        print(self.get_phase_banner())


    def get_player_banner(self):
        return f'\n{self.get_current_player().id}\'s turn!\n'


    def get_current_player(self):
        return self.players[self.current_player]


    def get_phase_banner(self):
        if self.phase == GamePhases.MAIN:
            return 'Cards: {}\nSelect an action to play: {}'\
                .format(self.get_current_player().get_hand_names(),
                        self.command_list.get_command_names())
        elif self.phase == GamePhases.WAIT_FOR_NOPE:
            return 'Type "n" to play "Nope" within 3 seconds'
        elif self.phase == GamePhases.SELECT_PLAYER_FOR_FAVOR:
            return f'Select a player to get a favor from: {self.get_other_players_ids()}'
        elif self.phase == GamePhases.SELECT_CARD_FOR_FAVOR:
            return f'Select the card you want to give: {self.favor_actions}'
        elif self.phase == GamePhases.SELECT_PLAYER_FOR_TWOS:
            return f'Select a player to steal a card from: {self.get_other_players_ids()}'
        elif self.phase == GamePhases.SELECT_PLAYER_FOR_THREES:
            return f'Select a player to steal a card from: {self.get_other_players_ids()}'
        elif self.phase == GamePhases.SELECT_CARD_FOR_THREES:
            return f'Select the card type you want to steal: {CardTypes.get_commands()}'
        else:
            return 'If you\'re reading this something\'s gone wrong :P'

    #################################################################
    # Cmd overrides
    #################################################################

    def preloop(self):
        print('Welcome to Exploding Kittens!\n')
        print('Dealt 1 defuse card to each player.')

        for player in self.players:
            player.draw_defuse_card()

        for player in self.players:
            player.draw_initial_cards()

        print(self.get_player_banner())
        self.start_of_phase()
        

    def default(self, line):
        player = self.get_current_player()

        if self.phase == GamePhases.MAIN:
            if line.lower() in self.command_list.get_command_names():
                self.play_turn(line.lower())
            else:
                print('Error: Please enter a valid move.')

        elif self.phase == GamePhases.WAIT_FOR_NOPE:
            if line.lower() == 'n':
                # Nope the previously played card
                pass

        elif self.phase == GamePhases.SELECT_PLAYER_FOR_FAVOR:
            if int(line) < len(self.players):
                self.favor_actions = self.players[int(line)].get_favor_actions()
                self.switch_player(int(line))
                self.phase = GamePhases.SELECT_CARD_FOR_FAVOR
            else:
                print('Error: Please enter a valid digit.')

        elif self.phase == GamePhases.SELECT_CARD_FOR_FAVOR:
            if int(line) < len(self.favor_actions):
                card_type = CardTypes.get_from_command(line)
                removed_card = player.remove_card(card_type)
                self.previous_player.add_card(removed_card)
                self.switch_to_previous_player()
                self.get_current_player().remove_card(CardTypes.FAVOR)
                self.phase = GamePhases.MAIN
            else:
                print('Error: Please enter a valid digit.')

        elif self.phase == GamePhases.SELECT_PLAYER_FOR_TWOS:
            if int(line) < len(self.players):
                player_index = self.players.index(line.lower())
                other_player = self.players[player_index]
                card_type = other_player.get_random_card_type_from_hand()
                removed_card = other_player.remove_card(card_type)
                player.add_card(removed_card)
                player.remove_card(self.combo_card_type, 2)
                self.phase = GamePhases.MAIN
            else:
                print('Error: Please enter a valid digit.')

        elif self.phase == GamePhases.SELECT_PLAYER_FOR_THREES:
            if int(line) < len(self.players):
                player_index = self.players.index(line.lower())
                self.chosen_player = self.players[player_index]
                self.phase = GamePhases.SELECT_CARD_FOR_THREES
            else:
                print('Error: Please enter a valid digit.')

        elif self.phase == GamePhases.SELECT_CARD_FOR_THREES:
            if int(line) < len(self.get_current_player.get_hand()):
                self.chosen_player.remove_card(CardTypes[line.lower()])
                player.remove_card(self.combo_card_type, 3)
                self.phase = GamePhases.MAIN
            else:
                print('Error: Please enter a valid digit.')
    

    # When the postcmd method returns True it ends the cmdloop
    def postcmd(self, stop, line):
        if len(self.players) > 1:
            self.start_of_phase()
        else:
            print(f'{self.players[0]} is the winner!')
            return True

    #################################################################
    # Cmd overrides end
    #################################################################

    def play_turn(self, command):
        player = self.get_current_player()
        move = MoveTypes(command)

        if move == MoveTypes.DRAW:
            card = player.draw_card()
            print(f'Drew {card.get_name()}!')

            if card.type == CardTypes.EXPLODING_KITTEN:
                # Check if the player has a defuse card
                if player.has_defuse():
                    player.remove_card(CardTypes.DEFUSE)
                    player.remove_card(CardTypes.EXPLODING_KITTEN)
                    print('Used a defuse card!')
                else:
                    self.explode()
                    print(f'No defuse cards left, {player.id} is out!')
                    self.next_player()
                    return

            player.turns_left -= 1
        elif move == MoveTypes.ATTACK:
            self.next_player(attack=True)
            player.remove_card(CardTypes.ATTACK)
        elif move == MoveTypes.FAVOR:
            self.phase = GamePhases.SELECT_PLAYER_FOR_FAVOR
        elif move == MoveTypes.NOPE:
            pass
        elif move == MoveTypes.SHUFFLE:
            self.deck.shuffle()
            player.remove_card(CardTypes.SHUFFLE)
        elif move == MoveTypes.SKIP:
            player.turns_left -= 1
            player.remove_card(CardTypes.SKIP)
        elif move == MoveTypes.SEE_THE_FUTURE:
            future_cards = self.deck.see_the_future()
            future_cards = [f'#{i}: {future_cards[i].get_name()}' for i in range(0, 3)]
            print(f'The future cards are {future_cards}')
            player.remove_card(CardTypes.SEE_THE_FUTURE)
        elif move == MoveTypes.TWO_OF_A_KIND:
            self.phase = GamePhases.SELECT_PLAYER_FOR_TWOS
            self.combo_card_type = command.card_type
        elif move == MoveTypes.THREE_OF_A_KIND:
            self.phase = GamePhases.SELECT_PLAYER_FOR_THREES
            self.combo_card_type = command.card_type

        if player.turns_left == 0:
            self.next_player()


    def get_other_players_ids(self):
        other_players = []

        for i in range(0, len(self.players)):
            if i != self.current_player:
                other_players.append(self.players[i].id.lower())
        
        return other_players


    def next_player(self, attack=False):
        self.current_player += 1
        if self.current_player > len(self.players) - 1:
            self.current_player = 0
        
        if attack:
            self.turns += 2
            self.get_current_player().turns_left = self.turns
        else:
            self.turns = 0
            self.get_current_player().turns_left = 1
        
        print(self.get_player_banner())


    def switch_player(self, player_index):
        self.previous_player = self.get_current_player()
        self.current_player = player_index
    

    def switch_to_previous_player(self):
        temp_player = self.get_current_player()
        self.current_player = self.previous_player
        self.previous_player = temp_player


    def explode(self):
        self.players.pop(self.current_player)
        self.current_player -= 1

    #################################################################
    # State class methods
    #################################################################

    def getCurrentPlayer():
        pass

    def getPossibleActions():
        pass

    def takeAction(action):
        pass

    def isTerminal():
        pass

    def getReward():
        pass

    

if __name__ == "__main__":
    player_types = (
        PlayerTypes.HUMAN,
        PlayerTypes.HUMAN,
        PlayerTypes.HUMAN,
        PlayerTypes.HUMAN
    )
    game = ExplodingKittens(player_types)
    game.cmdloop()