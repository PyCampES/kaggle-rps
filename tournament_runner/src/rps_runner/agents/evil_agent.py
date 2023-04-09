from collections import deque, Counter
from dataclasses import dataclass
from enum import IntEnum
import logging
import random
import typing as t

import numpy as np
import pandas as pd
import structlog

structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(logging.INFO))
logger = structlog.get_logger()


class Actions(IntEnum):
    ROCK = 0
    PAPER = 1
    SCISSORS = 2


def get_winning_action(action: Actions):
    return Actions((action + 1) % 3)


def get_random_action():
    return Actions(random.randint(0, 2))


class Strategy(t.Protocol):
    def record_observation(self, observation) -> None:
        ...

    def get_next_action(self) -> Actions:
        ...


@dataclass
class DummyStrategy:
    last_opponent_action: Actions = None

    def record_observation(self, observation):
        if observation.step > 0:
            self.last_opponent_action = Actions(observation.lastOpponentAction)

    def get_next_action(self):
        if self.last_opponent_action is None:
            return Actions.ROCK
        else:
            return get_winning_action(self.last_opponent_action)


@dataclass
class CopycatStrategy:
    last_opponent_action: Actions = None

    def record_observation(self, observation):
        if observation.step > 0:
            self.last_opponent_action = Actions(observation.lastOpponentAction)

    def get_next_action(self):
        if self.last_opponent_action is None:
            return Actions.ROCK
        else:
            return self.last_opponent_action


@dataclass
class PastNStrategy:
    past_opponent_actions = deque(maxlen=50)

    def record_observation(self, observation):
        if observation.step > 0:
            self.past_opponent_actions.append(Actions(observation.lastOpponentAction))

    def get_next_action(self):
        counts = Counter(self.past_opponent_actions)
        if not (most_common := counts.most_common()):
            return get_random_action()

        if len(most_common) > 1:
            # Balanced probabilities
            # XXX: Get any of the most common past actions
            next_action = get_winning_action(most_common[0][0])
        else:
            # One action is more likely than the others
            next_action = get_winning_action(most_common[0][0])

        return next_action


def compute_transition_matrix(actions_dict):
    # Forgive me
    df = (
        pd.DataFrame(actions_dict)
        .apply(pd.Series.value_counts)
        .reindex([0, 1, 2])
        .fillna(0)
    )
    return (df / 10).values.T


@dataclass
class TransitionMatrixStrategy:
    last_score: int = 0
    last_own_actions = deque(maxlen=10)
    # Keys are my moves, queues host opponent responses
    opponent_transitions = {
        Actions.ROCK: deque([Actions.PAPER] * 10, maxlen=10),
        Actions.PAPER: deque([Actions.SCISSORS] * 10, maxlen=10),
        Actions.SCISSORS: deque([Actions.ROCK] * 10, maxlen=10),
    }

    def _get_most_likely_opponent_action(self, self_action):
        probs = compute_transition_matrix(self.opponent_transitions)[self_action]
        most_likely_opponent_action = Actions(np.argmax(probs))
        logger.debug(
            f"... most likely, opponent will play {most_likely_opponent_action.name} (prob {np.max(probs)})"
        )
        return most_likely_opponent_action

    def record_observation(self, observation):
        logger.debug(observation)
        if observation.step > 0:
            last_opponent_action = observation.lastOpponentAction
            previous_own_action = self.last_own_actions[-1]

            logger.debug(f"Previous own action was {previous_own_action.name}")
            logger.debug(f"Opponent reaction was {last_opponent_action.name}")

            if observation.step > 1:
                reference_own_action = self.last_own_actions[-2]
                logger.debug(
                    f"Expected probability was {compute_transition_matrix(self.opponent_transitions)[reference_own_action.value, last_opponent_action.value]}"
                )

                # Check score
                if observation["reward"] < self.last_score:
                    # We lost!
                    # Record transition
                    logger.debug("We lost :(")
                    self.opponent_transitions[reference_own_action].append(
                        last_opponent_action
                    )
                    logger.debug(
                        f"Adjusted transitions are {self.opponent_transitions[previous_own_action]}"
                    )
                    logger.debug(
                        f"Adjusted probability is {compute_transition_matrix(self.opponent_transitions)[previous_own_action.value, last_opponent_action.value]}"
                    )
                else:
                    # Tie, or we won
                    logger.debug("We WON! Or tie")
                    logger.debug("Did not touch probability")

            # Record score regardless
            self.last_score = observation["reward"]
        else:
            logger.debug("Don't know what to do, waiting")

    def get_next_action(self):
        if not self.last_own_actions:
            next_action = get_random_action()
        else:
            likely_opponent_action = self._get_most_likely_opponent_action(
                self.last_own_actions[-1]
            )
            next_action = get_winning_action(likely_opponent_action)

        logger.debug(f":: Play {next_action.name}!")
        self.last_own_actions.append(next_action)
        return next_action


@dataclass
class StrategyPicker:
    max_steps: int
    initial_strategy: Strategy

    @classmethod
    def from_config(cls, configuration):
        return cls(max_steps=configuration["episodeSteps"])

    def record_result(self, observation):
        ...

    def get_strategy(self):
        return self.initial_strategy


def dummy_agent(observation, configuration):
    current_strategy = CopycatStrategy()

    current_strategy.record_observation(observation)
    return current_strategy.get_next_action()


def evil_agent(
    observation,
    configuration,
    strategy_picker=StrategyPicker(1000, TransitionMatrixStrategy()),
):
    strategy_picker.record_result(observation)
    current_strategy = strategy_picker.get_strategy()

    current_strategy.record_observation(observation)
    return current_strategy.get_next_action()


agent = evil_agent
