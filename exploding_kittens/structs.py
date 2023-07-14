from enum import Enum, auto

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


class Command:
    def __init__(self, move_type, card_type=None):
        self.move_type = move_type
        self.card_type = card_type


class CommandList:
    def __init__(self):
        self.commands = []
    
    def add_command(self, command):
        self.commands.append(command)
    
    def get_command_names(self):
        names = []

        for com in self.commands:
            name = com.move_type.value
            if com.card_type is not None:
                name += ' ' + com.card_type.value.command
            names.append(name)

        return names
    

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

    def get_commands(self):
        return [card_type.command for card_type in self]
    
    def get_from_command(self, command):
        for card_type in self:
            if card_type.command == command:
                return card_type
        return None

class PlayerTypes(Enum):
    HUMAN = 'human'
    RANDOM = 'random'

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

def lower_list(list):
    return [elm.lower() for elm in list]