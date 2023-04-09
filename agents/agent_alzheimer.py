import random
from dataclasses import dataclass
from collections import deque, defaultdict
from enum import Enum
import math

MEMORY_LENGTH = 5
hands_buffer = deque([], maxlen=MEMORY_LENGTH)
patterns_memory = defaultdict(lambda: defaultdict(int))
my_last_action = None


class Sign(Enum):
    ROCK = 0
    PAPER = 1
    SCISSORS = 2

    def beats(self, other_sign):
        left_move = self.value
        right_move = other_sign.value
        delta = (
            right_move - left_move
            if (left_move + right_move) % 2 == 0
            else left_move - right_move
        )
        return 0 if delta == 0 else math.copysign(1, delta)

    @property
    def beater(self):
        if self == Sign.ROCK:
            return Sign.PAPER
        elif self == Sign.PAPER:
            return Sign.SCISSORS
        elif self == Sign.SCISSORS:
            return Sign.ROCK


@dataclass
class Hand:
    mine: Sign
    adversary: Sign

    @property
    def score(self):
        return self.mine.beats(self.adversary)

    def __hash__(self):
        return hash(repr(self))


def dict_argmax(d: dict):
    if d:  # dict is not empty
        return max(d, key=d.get)
    else:
        return None


def agent_alzheimer(observation, configuration):
    global patterns_memory, hands_buffer, my_last_action

    # Special case for the first MEMORY_LENGTH+1 steps
    if observation.step <= MEMORY_LENGTH:
        my_last_action = random.randint(0, 2)
        if observation.step > 0:
            hands_buffer.append(Hand(mine=Sign(my_last_action), adversary=Sign(observation.lastOpponentAction)))
        return my_last_action

    # Update the hands buffer
    my_last_sign = Sign(my_last_action)
    adversary_last_sign = Sign(observation.lastOpponentAction)
    hands_buffer.append(Hand(mine=my_last_sign, adversary=adversary_last_sign))

    # Update patterns memory
    buffer_as_list = list(hands_buffer)
    old_hands = tuple(buffer_as_list[:-1])
    patterns_memory[old_hands][adversary_last_sign.beater] += 1

    # Try to find the next best hand
    current_hand = tuple(buffer_as_list[1:])
    argmax = dict_argmax(patterns_memory[current_hand])
    if argmax:  # Entry exists
        return argmax.value
    else:
        return random.randint(0, 2)
