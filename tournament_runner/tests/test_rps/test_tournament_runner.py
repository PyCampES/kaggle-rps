from kaggle_environments import evaluate, make

from rps_runner.agents.paper import constant_play_agent_1
from rps_runner.agents.rocks import constant_play_agent_0
from rps_runner.agents.scissor import constant_play_agent_2
from rps_runner.tournament_runner import (
    GameResult,
    run_tournament,
    import_agents,
    DEFAULT_AGENT_DIR,
)


def test_evaluate():
    env = make("rps", configuration={"episodeSteps": 100})
    output = env.run(
        [constant_play_agent_1, constant_play_agent_0],
    )
    print(output)
    assert output


def test_game_result():
    output = evaluate(
        "rps",
        [constant_play_agent_2, constant_play_agent_0],
    )
    result = GameResult(agent_a="scissor", agent_b="rocks", output=output)
    assert result.winner == "rocks"
    assert result.loser == "scissor"


def test_agents():
    agents = import_agents(DEFAULT_AGENT_DIR)
    results = run_tournament(agents, ["evil_agent", "paper"])
    assert results


def test_game_result_tie():
    output = evaluate(
        "rps",
        [constant_play_agent_2, constant_play_agent_2],
    )
    result = GameResult(agent_a="scissor1", agent_b="scissor2", output=output)
    assert result.is_tie
