from enum import Enum, auto

class Action:
    def __init__(self, player, move_type=None, played_card_type=None, requested_player=None, requested_card_type=None, given_card=None):
        self.player = player
        self.move_type = move_type
        self.played_card_type = played_card_type
        self.requested_player = requested_player
        self.requested_card_type = requested_card_type
        self.given_card = given_card

    def as_command(self):
        str_out = self.move_type.value

    def __str__(self):
        str_out = f'player: {self.player}\nmove_type: {self.move_type}\n'

        if self.played_card_type is not None:
            str_out += f'card_type: {self.played_card_type}\n'
        if self.requested_player is not None:
            str_out += f'requested_player: {self.requested_player}\n'
        if self.requested_card_type is not None:
            str_out += f'requested_card_type: {self.requested_card_type}\n'

        return str_out
    
    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.player == other.player \
        and self.move_type == other.move_type \
        and self.played_card_type == other.played_card_type \
        and self.requested_player == other.requested_player \
        and self.requested_card_type == other.requested_card_type


    def __hash__(self):
        return hash((self.player, self.move_type, self.played_card_type, self.requested_player, self.requested_card_type))

    @staticmethod
    def from_command(player, command):
        params = command.split(' ')
        move_type = MoveTypes(params[0])
        played_card_type = None

        if move_type == MoveTypes.TWO_OF_A_KIND or \
        move_type == MoveTypes.THREE_OF_A_KIND:
            played_card_type = CardTypes.get_from_command(params[1])

        return Action(player, move_type, played_card_type)
    

class ActionList:
    def __init__(self):
        self.commands = []
    
    def add_command(self, command):
        self.commands.append(command)

    def get_command_names(self):
        names = []

        for com in self.commands:
            name = com.move_type.value
            if com.played_card_type is not None:
                name += ' ' + com.played_card_type.value.command
            names.append(name)

        return names
    
    def as_list(self):
        return self.commands
    
    def __len__(self):
        return len(self.commands)
    
    def __getitem__(self, key):
        return self.commands[key]


class MoveTypes(Enum):
    DRAW = 'draw'
    ATTACK = 'attack'
    FAVOR = 'favor'
    NOPE = 'nope'
    SHUFFLE = 'shuffle'
    SKIP = 'skip'
    SEE_THE_FUTURE = 'future'
    TWO_OF_A_KIND = 'two'
    THREE_OF_A_KIND = 'three'

    @staticmethod
    def as_int(command):
        i = 0
        for member in MoveTypes:
            if member.value == command:
                return i
            i += 1
        return -1


class Card:
    def __init__(self, card_type):
        self.type = card_type
    
    def get_name(self):
        return self.type.value.name
    
    def get_command(self):
        return self.type.value.command
    
    def get_move_type(self):
        return self.type.value.move_type


class CardTypeValue:
    def __init__(self, name, command=None, move_type=None):
        self.name = name
        self.command = command
        self.move_type = move_type


class CardTypes(Enum):
    EXPLODING_KITTEN    = CardTypeValue('Exploding Kitten')
    DEFUSE              = CardTypeValue('Defuse', 'defuse')
    ATTACK              = CardTypeValue('Attack', 'attack', MoveTypes.ATTACK)
    FAVOR               = CardTypeValue('Favor', 'favor', MoveTypes.FAVOR)
    NOPE                = CardTypeValue('Nope', 'nope', MoveTypes.NOPE)
    SHUFFLE             = CardTypeValue('Shuffle', 'shuffle', MoveTypes.SHUFFLE)
    SKIP                = CardTypeValue('Skip', 'skip', MoveTypes.SKIP)
    SEE_THE_FUTURE      = CardTypeValue('See The Future', 'future', MoveTypes.SEE_THE_FUTURE)
    RAINBOW_CAT         = CardTypeValue('Rainbow-Ralphing Cat', 'rainbow')
    POTATO_CAT          = CardTypeValue('Hairy Potato Cat', 'potato')
    TACOCAT             = CardTypeValue('Tacocat', 'tacocat')
    CATTERMELON         = CardTypeValue('Cattermelon', 'melon')
    BEARD_CAT           = CardTypeValue('Beard Cat', 'beard')

    @staticmethod
    def get_commands():
        return [card_type.command for card_type in CardTypes]
    
    @staticmethod
    def get_from_command(command):
        for card_type in CardTypes:
            if card_type.value.command == command:
                return card_type
        return None
    
    @staticmethod
    def get_playable_types():
        types_out = []

        for card_type in CardTypes:
            if card_type != CardTypes.EXPLODING_KITTEN:
                types_out.append(card_type)
        
        return types_out

class PlayerTypes(Enum):
    HUMAN = auto()
    RANDOM = auto()
    MCTS = auto()


class GamePhases(Enum):
    MAIN = auto()
    WAIT_FOR_NOPE = auto()
    SELECT_PLAYER_FOR_FAVOR = auto()
    SELECT_CARD_FOR_FAVOR = auto()
    SELECT_PLAYER_FOR_TWOS = auto()
    SELECT_PLAYER_FOR_THREES = auto()
    SELECT_CARD_FOR_THREES = auto()
    SELECT_TWO_CARDS = auto()
    SELECT_THREE_CARDS = auto()