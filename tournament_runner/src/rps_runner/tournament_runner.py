from __future__ import annotations

import logging
import os
import shutil
from dataclasses import dataclass, field
from functools import total_ordering
from os import getenv
from pathlib import Path
from pydoc import locate
from typing import TypeAlias, Literal, Any, Callable, cast

from kaggle_environments import evaluate

list_names = [
    "reactionary",
    "counter_reactionary",
    "statistical",
]
logger = logging.getLogger(__name__)
list_agents = [agent_name + ".py" for agent_name in list_names]


AgentFunc: TypeAlias = Callable[[Any, Any], Literal[0, 1, 2]]
Agents: TypeAlias = dict[str, AgentFunc]
ROUNDS_PER_GAME = 100
GAMES_BETWEEN_AGENTS = 1

DEFAULT_AGENT_DIR = Path(__file__).parent / "agents"
AGENT_DIR = os.getenv("AGENT_DIR", "")
COMPETE_AGENT_DIR = os.getenv("COMPETE_AGENT_DIR", "")

def as_import_path(agent: str) -> str:
    return f"rps_runner.agents.{agent}.agent"

def as_compete_path_live(agent: str) -> Path:
    assert COMPETE_AGENT_DIR, "COMPETE_AGENT_DIR not set"
    return Path(COMPETE_AGENT_DIR) / f"{agent}.py"


def as_compete_import(agent_path: Path):
    return f"compete_agents.{agent_path.stem}.agent"

def import_agents(agent_dir: Path, is_compete_path: bool = False) -> Agents:
    name_to_func = {}
    for agent_path in agent_dir.glob("*.py"):
        agent_name = agent_path.stem
        if not agent_path.is_file() or agent_name.startswith("_"):
            continue
        import_path = as_compete_import(agent_path) if is_compete_path else as_import_path(agent_name)
        agent_func = locate(import_path)
        assert agent_func, f"unable to find agent @ {import_path}"
        name_to_func[agent_name] = agent_func
    return cast(Agents, name_to_func)


def find_matches(agents: Agents) -> list[tuple[str, str]]:
    list_of_games = []
    agent_names = list(agents.keys())
    for GAME_NR in range(GAMES_BETWEEN_AGENTS):
        for agent_a in agent_names:
            for agent_b in agent_names:
                if agent_a != agent_b:
                    list_of_games.append((agent_a, agent_b))
    return list_of_games


@dataclass
class GameResult:
    agent_a: str
    agent_b: str
    output: list[list[float]]

    def __post_init__(self):
        if self._result_score is None:
            logger.warning(f"agent score None: {self.agent_a}")
            self.output[0].pop(0)
            self.agent_a, self.agent_b = self.agent_b, self.agent_a
            assert self._result_score

    @property
    def _result_score(self):
        return self.output[0][0]

    @property
    def is_tie(self):
        return self._result_score == 0

    @property
    def winner(self):
        assert not self.is_tie
        return self.agent_a if self._result_score > 0 else self.agent_b

    @property
    def loser(self):
        assert not self.is_tie
        return self.agent_a if self.winner == self.agent_b else self.agent_b

    def is_winner(self, agent: str) -> bool:
        return not self.is_tie and self.winner == agent

    def is_loser(self, agent: str) -> bool:
        return not self.is_tie and self.winner != agent


@total_ordering
@dataclass
class AgentResult:
    name: str
    games: list[GameResult] = field(default_factory=list)

    @property
    def wins(self) -> int:
        return len([game for game in self.games if game.is_winner(self.name)])

    @property
    def loses(self) -> int:
        return len([game for game in self.games if game.is_loser(self.name)])

    @property
    def ties(self) -> int:
        return len([game for game in self.games if game.is_tie])

    def __str__(self):
        return f"Agent: {self.name}, W={self.wins}, T={self.ties}, L={self.loses}"

    def __lt__(self, other: AgentResult):
        if not isinstance(other, AgentResult):
            raise TypeError
        return self.wins > other.wins


def play_game(agents: Agents, match_agents: tuple[str, str]) -> GameResult:
    agent_a, agent_b = match_agents
    agent_a_func = agents[agent_a]
    agent_b_func = agents[agent_b]
    output = evaluate(
        "rps",
        [agent_a_func, agent_b_func],
        configuration={"episodeSteps": ROUNDS_PER_GAME},
    )
    return GameResult(agent_a, agent_b, output)


def run_tournament(agents: Agents, agents_only: list[str] | None = None):
    agents_only = agents_only or list(agents.keys())
    agents = {agent: agent_func for agent, agent_func in agents.items() if agent in agents_only}
    agent_names = list(agents.keys())
    logger.info(f"creating tournament for {agent_names}")
    output: dict[str, AgentResult] = {name: AgentResult(name) for name in agent_names}
    list_of_games = find_matches(agents)
    print(f"will play: {len(list_of_games)} games")
    logger.info("tournament start")

    for player1, player2 in list_of_games:
        try:
            game = play_game(agents, (player1, player2))
        except AssertionError as e:
            print(e)
            raise e
        output[player1].games.append(game)
        output[player2].games.append(game)
    logger.info("tournament end")
    agent_ranking = sorted(output.values())
    for i, agent_rank in enumerate(agent_ranking, start=1):
        print(f"# {i}. {agent_rank}")
    return agent_ranking

_ranking: list[AgentResult] = []


def select_player_agents(path: Path):
    dest_path = COMPETE_AGENT_DIR
    assert dest_path and Path(dest_path).exists()
    dest_path = Path(dest_path)
    for file in dest_path.glob("*.py"):
        file.unlink()
    (dest_path / "__init__.py").write_text("")

    for py_file in path.rglob("*.py"):
        player = py_file.parent.name
        agent_path = dest_path / f"{player}_{py_file.stem}.py"
        logger.info(f"adding agent for {player}")
        shutil.copy(py_file, agent_path)
    return dest_path



def full_run():
    if AGENT_DIR and Path(AGENT_DIR).exists():
        agent_dir = select_player_agents(Path(AGENT_DIR))
        agents = import_agents(agent_dir, is_compete_path=True)
    else:
        agents = import_agents(DEFAULT_AGENT_DIR, is_compete_path=False)
    new_ranking = run_tournament(agents)
    global _ranking
    _ranking = new_ranking
    return new_ranking


def get_results() -> list[AgentResult]:
    if not _ranking:
        full_run()
    return _ranking


if __name__ == "__main__":
    format = "%(asctime)s.%(msecs)03d %(levelname)-7s %(threadName)-s %(name)-s %(lineno)-s %(message)-s"
    logging.basicConfig(level=logging.INFO, format=format)
    results = full_run()
    print(results)
