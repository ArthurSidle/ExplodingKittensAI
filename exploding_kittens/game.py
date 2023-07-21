# Adapted from https://codereview.stackexchange.com/questions/196533/simulate-a-simplified-version-of-exploding-kittens-in-python
from cmd import Cmd
from structs import *
from deck import *
from player import *
from mcts import mcts


class ExplodingKittens(Cmd):
    def __init__(self, player_types):
        super().__init__(self)
        self.phase = GamePhases.MAIN
        self.deck, self.players = self.start_game(player_types)
        self.current_player = 0

        self.command_list = ActionList()
        self.int_commands = []
        self.chosen_player = None
        self.turns = 0
        self.favor_actions = None
        self.combo_card_type = None

        print('Welcome to Exploding Kittens!\n')
        print('Dealt 1 defuse card to each player.')

        for player in self.players:
            player.draw_defuse_card()

        for player in self.players:
            player.draw_initial_cards()


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


    def print_player_banner(self):
        print(f'\n{self.get_current_player().id}\'s turn!\n')


    def get_current_player(self):
        return self.players[self.current_player]
    

    def get_previous_player(self):
        return self.players[self.previous_player]


    def get_phase_banner(self):
        if self.phase == GamePhases.MAIN:
            return 'Cards: {}\nSelect an action to play: {}'\
                .format(self.get_current_player().get_hand_names(),
                        self.command_list.get_command_names())
        elif self.phase == GamePhases.WAIT_FOR_NOPE:
            return 'Type "n" to play "Nope", otherwise, press enter.'
        elif self.phase == GamePhases.SELECT_PLAYER_FOR_FAVOR:
            return f'Select a player to get a favor from: {self.int_commands}'
        elif self.phase == GamePhases.SELECT_CARD_FOR_FAVOR:
            return f'Select the card you want to give: {self.int_commands}'
        elif self.phase == GamePhases.SELECT_PLAYER_FOR_TWOS:
            return f'Select a player to steal a card from: {self.int_commands}'
        elif self.phase == GamePhases.SELECT_PLAYER_FOR_THREES:
            return f'Select a player to steal a card from: {self.int_commands}'
        elif self.phase == GamePhases.SELECT_CARD_FOR_THREES:
            return f'Select the card type you want to steal: {self.int_commands}'
        else:
            return 'If you\'re reading this something\'s gone wrong :P'

    #################################################################
    # Cmd overrides
    #################################################################

    def preloop(self):
        self.print_player_banner()
        self.start_of_phase()
        

    def default(self, line):
        self.take_command(line=line)


    # When the postcmd method returns True it ends the cmdloop
    def postcmd(self, stop, line):
        if len(self.players) > 1:
            if self.get_current_player().type != PlayerTypes.HUMAN:
                return True
            self.start_of_phase()
        else:
            print(f'{self.players[0].id} is the winner!')
            return True

    #################################################################
    # Cmd overrides end
    #################################################################

    def take_command(self, line='', action=None):
        player = self.get_current_player()

        if self.phase == GamePhases.MAIN:
            if line.lower() in self.command_list.get_command_names():
                self.play_turn(line=line.lower())
            elif action is not None:
                self.play_turn(action=action)
            else:
                print('Error: Please enter a valid move.')

        elif self.phase == GamePhases.WAIT_FOR_NOPE:
            if line.lower() == 'n':
                # Nope the previously played card
                pass

        elif self.phase == GamePhases.SELECT_PLAYER_FOR_FAVOR:
            if line != '' and int(line) < len(self.int_commands) and int(line) >= 0:
                self.favor_commands = self.int_commands[int(line)].get_favor_commands()
                self.switch_player(self.int_commands[int(line)])
                self.phase = GamePhases.SELECT_CARD_FOR_FAVOR
                self.int_commands = IntCommandList(self.favor_commands)
            else:
                print('Error: Please enter a valid digit.')

        elif self.phase == GamePhases.SELECT_CARD_FOR_FAVOR:
            if action is not None:
                card_type = action.given_card
                removed_card = player.remove_card(card_type)
                self.get_previous_player().add_card(removed_card)
                self.switch_to_previous_player()
                self.get_current_player().remove_card(CardTypes.FAVOR)
                self.phase = GamePhases.MAIN
            elif int(line) < len(self.int_commands) and int(line) >= 0:
                card_type = self.int_commands[int(line)]
                removed_card = player.remove_card(card_type)
                self.get_previous_player().add_card(removed_card)
                self.switch_to_previous_player()
                self.get_current_player().remove_card(CardTypes.FAVOR)
                self.phase = GamePhases.MAIN
            else:
                print('Error: Please enter a valid digit.')

        elif self.phase == GamePhases.SELECT_PLAYER_FOR_TWOS:
            if int(line) < len(self.int_commands):
                requested_player = self.int_commands[int(line)]
                self.play_twos(self.combo_card_type, requested_player)
                self.phase = GamePhases.MAIN
            else:
                print('Error: Please enter a valid digit.')

        elif self.phase == GamePhases.SELECT_PLAYER_FOR_THREES:
            if int(line) < len(self.int_commands):
                self.chosen_player = self.int_commands[int(line)]
                self.int_commands = IntCommandList(CardTypes.get_playable_types())
                self.phase = GamePhases.SELECT_CARD_FOR_THREES
            else:
                print('Error: Please enter a valid digit.')

        elif self.phase == GamePhases.SELECT_CARD_FOR_THREES:
            if int(line) < len(self.int_commands):
                requested_card_type = self.int_commands[int(line)]
                self.play_threes(self.combo_card_type, self.chosen_player, requested_card_type)
                self.phase = GamePhases.MAIN
            else:
                print('Error: Please enter a valid digit.')


    def play_turn(self, line='', action=None):
        player = self.get_current_player()

        # splits command into dictionary
        if action is None:
            action = Action.from_command(self.get_current_player(), line)


        if action.move_type == MoveTypes.DRAW:
            card = player.draw_card()
            print(f'Drew {card.get_name()}!')

            if card.type == CardTypes.EXPLODING_KITTEN:
                # Check if the player has a defuse card
                if player.has_card(CardTypes.DEFUSE):
                    player.remove_card(CardTypes.DEFUSE)
                    player.remove_card(CardTypes.EXPLODING_KITTEN)
                    self.deck.add_kitten()
                    print('Used a defuse card!')
                else:
                    self.explode()
                    print(f'No defuse cards left, {player.id} is out!')
                    self.next_player()
                    return
                
            player.turns_left -= 1

        elif action.move_type == MoveTypes.ATTACK:
            print('Played attack!')
            self.next_player(attack=True)
            player.remove_card(CardTypes.ATTACK)

        elif action.move_type == MoveTypes.FAVOR:
            print('Played favor!')
            if action.requested_player is not None:
                self.switch_player(action.requested_player)
                self.phase = GamePhases.SELECT_CARD_FOR_FAVOR
                self.int_commands = IntCommandList(self.get_current_player().get_favor_commands())
            else:
                self.int_commands = IntCommandList(self.get_other_players())
                self.phase = GamePhases.SELECT_PLAYER_FOR_FAVOR
            
        elif action.move_type == MoveTypes.NOPE:
            print('Played nope!')

        elif action.move_type == MoveTypes.SHUFFLE:
            print('Played shuffle!')
            self.deck.shuffle()
            player.remove_card(CardTypes.SHUFFLE)

        elif action.move_type == MoveTypes.SKIP:
            print('Played skip!')
            player.turns_left -= 1
            player.remove_card(CardTypes.SKIP)

        elif action.move_type == MoveTypes.SEE_THE_FUTURE:
            print('Played see the future!')
            future_cards = self.deck.see_the_future()
            future_cards = [f'#{i}: {future_cards[i].get_name()}' for i in range(0, 3)]
            print(f'The future cards are {future_cards}')
            player.remove_card(CardTypes.SEE_THE_FUTURE)

        elif action.move_type == MoveTypes.TWO_OF_A_KIND:
            print('Played two of a kind!')
            if action.requested_player is not None:
                self.play_twos(action.played_card_type, action.requested_player)
            else:
                self.phase = GamePhases.SELECT_PLAYER_FOR_TWOS
                self.combo_card_type = action.played_card_type
                self.int_commands = IntCommandList(self.get_other_players())

        elif action.move_type == MoveTypes.THREE_OF_A_KIND:
            print('Played three of a kind!')
            if action.requested_player is not None:
                self.play_threes(action.played_card_type, action.requested_player, action.requested_card_type)
            else:
                self.phase = GamePhases.SELECT_PLAYER_FOR_THREES
                self.combo_card_type = action.played_card_type
                self.int_commands = IntCommandList(self.get_other_players())

        if player.turns_left == 0:
            self.next_player()


    def play_twos(self, played_card_type, requested_player):
        requested_card_type = requested_player.get_random_card_type_from_hand()
        removed_card = requested_player.remove_card(requested_card_type)
        self.get_current_player().add_card(removed_card)
        self.get_current_player().remove_card(played_card_type, 2)
        print(f'Stole {removed_card.get_name()} from {requested_player.id}!')


    def play_threes(self, played_card_type, requested_player, requested_card_type):
        if requested_player.has_card(requested_card_type):
            removed_card = requested_player.remove_card(requested_card_type)
            self.get_current_player().add_card(removed_card)
            print(f'Stole {removed_card.get_name()} from {requested_player.id}!')
        else:
            print(f'{requested_player.id} did not have {requested_card_type.value.name}!')

        self.get_current_player().remove_card(self.combo_card_type, 3)


    def get_other_players(self):
        other_players = []

        for player in self.players:
            if player != self.get_current_player():
                other_players.append(player)
        
        return other_players


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

        if self.get_current_player().type == PlayerTypes.HUMAN:
            self.print_player_banner()


    def switch_player(self, player):
        self.previous_player = self.current_player
        self.current_player = self.players.index(player)
    

    def switch_to_previous_player(self):
        temp_player = self.get_current_player()
        self.current_player = self.previous_player
        self.previous_player = temp_player


    def explode(self):
        self.players.pop(self.current_player)
        self.current_player -= 1



class EKState():
    def __init__(self, game: ExplodingKittens):
        self.game = game

    def getCurrentPlayer(self):
        return self.game.current_player

    def getPossibleActions(self):
        if self.game.phase == GamePhases.MAIN:
            action_list = self.game.get_current_player().get_commands(True).as_list()
        else:
            action_list = self.game.get_current_player().get_favor_commands().as_list()
        return action_list

    def takeAction(self, action):
        self.game.take_command(action=action)
        return EKState(self.game)

    def isTerminal(self):
        return len(self.game.players) <= 1

    def getReward(self):
        return 1
    

class IntCommandList:
    def __init__(self, list_in):
        self.obj_list = list_in
        if len(self.obj_list) != 0:
            if self.obj_list[0].__class__ is Player:
                self.obj_type = 'player'
            elif self.obj_list is ActionList:
                self.obj_type = 'card'
            else:
                self.obj_type = ''
        else:
            self.obj_type = ''

    def __getitem__(self, key):
        return self.obj_list[key]
    
    def __len__(self):
        return len(self.obj_list)

    def __repr__(self):
        str_out = ''

        for i in range (0, len(self.obj_list)):
            if self.obj_type == 'player':
                name = self.obj_list[i].id
            elif self.obj_type == 'card':
                name = self.obj_list[i].given_card.get_name()

            str_out += f'{i}: {name}, '
        
        return str_out
    

if __name__ == "__main__":
    for i in range(0, 10):
        player_types = (
            PlayerTypes.MCTS,
            PlayerTypes.RANDOM,
            PlayerTypes.RANDOM,
            PlayerTypes.RANDOM
        )
        game = ExplodingKittens(player_types)
        state = EKState(game)
        searcher = mcts(timeLimit=1000)

        while len(game.players) > 1:
            player_type = game.get_current_player().type

            if player_type == PlayerTypes.HUMAN:
                game.cmdloop()
            elif player_type == PlayerTypes.RANDOM:
                actions = state.getPossibleActions()
                action_i = random.randint(0, len(actions) - 1)
                if len(game.players) <= 1: break
                state = state.takeAction(actions[action_i])
            elif player_type == PlayerTypes.MCTS:
                try:
                    best_action = searcher.search(state)
                except Exception:
                    pass
                if len(game.players) <= 1: break
                state = state.takeAction(best_action)