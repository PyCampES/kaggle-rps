from pathlib import Path

from rps_runner.api import as_html
from rps_runner.tournament_runner import GameResult, AgentResult

dummy_data = [
    AgentResult(
        name="statistical",
        games=[
            GameResult(
                agent_a="scissor", agent_b="statistical", output=[[-99.0, 99.0]]
            ),
            GameResult(
                agent_a="statistical", agent_b="scissor", output=[[99.0, -99.0]]
            ),
            GameResult(agent_a="statistical", agent_b="rocks", output=[[98.0, -98.0]]),
            GameResult(agent_a="statistical", agent_b="paper", output=[[97.0, -97.0]]),
            GameResult(agent_a="rocks", agent_b="statistical", output=[[-98.0, 98.0]]),
            GameResult(agent_a="paper", agent_b="statistical", output=[[-97.0, 97.0]]),
        ],
    ),
    AgentResult(
        name="scissor",
        games=[
            GameResult(
                agent_a="scissor", agent_b="statistical", output=[[-99.0, 99.0]]
            ),
            GameResult(agent_a="scissor", agent_b="rocks", output=[[-99.0, 99.0]]),
            GameResult(agent_a="scissor", agent_b="paper", output=[[99.0, -99.0]]),
            GameResult(
                agent_a="statistical", agent_b="scissor", output=[[99.0, -99.0]]
            ),
            GameResult(agent_a="rocks", agent_b="scissor", output=[[99.0, -99.0]]),
            GameResult(agent_a="paper", agent_b="scissor", output=[[-99.0, 99.0]]),
        ],
    ),
    AgentResult(
        name="rocks",
        games=[
            GameResult(agent_a="scissor", agent_b="rocks", output=[[-99.0, 99.0]]),
            GameResult(agent_a="statistical", agent_b="rocks", output=[[98.0, -98.0]]),
            GameResult(agent_a="rocks", agent_b="scissor", output=[[99.0, -99.0]]),
            GameResult(agent_a="rocks", agent_b="statistical", output=[[-98.0, 98.0]]),
            GameResult(agent_a="rocks", agent_b="paper", output=[[-99.0, 99.0]]),
            GameResult(agent_a="paper", agent_b="rocks", output=[[99.0, -99.0]]),
        ],
    ),
    AgentResult(
        name="paper",
        games=[
            GameResult(agent_a="scissor", agent_b="paper", output=[[99.0, -99.0]]),
            GameResult(agent_a="statistical", agent_b="paper", output=[[97.0, -97.0]]),
            GameResult(agent_a="rocks", agent_b="paper", output=[[-99.0, 99.0]]),
            GameResult(agent_a="paper", agent_b="scissor", output=[[-99.0, 99.0]]),
            GameResult(agent_a="paper", agent_b="statistical", output=[[-97.0, 97.0]]),
            GameResult(agent_a="paper", agent_b="rocks", output=[[99.0, -99.0]]),
        ],
    ),
]


def test_as_html():
    path = Path(__file__).with_name("results.html")
    html = as_html(dummy_data)
    path.write_text(html)
