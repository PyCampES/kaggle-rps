
import kaggle_environments

from typing import Union

from fastapi import FastAPI

from pathlib import Path

from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select

import logging

import datetime


from dotenv import dotenv_values

config = dotenv_values(".env.public")

class GameResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    player: str
    enemy: str
    result: Optional[int] = None
    created_at: str

engine = create_engine("sqlite:///database.db")


SQLModel.metadata.create_all(engine)

app = FastAPI()


AGENTS_PATH = config['AGENTS_PATH']
base_path = Path(AGENTS_PATH)

@app.get("/")
def read_root():
    return {"Hello": "World"}

def fight_one(agent1_path: str, agent2_path: str):

    environment = kaggle_environments.make("rps", debug=True)

    environment.reset()

    observations = environment.run([str(agent1_path), str(agent2_path)])

    return observations[-1][0]['reward']


def list_agents():
    agentlist = base_path.rglob('*')

    newest_agents = [agent for agent in agentlist if agent.is_file()]

    return newest_agents

def fight(player_id: int, agent_path: Path):

    results = {}

    agents = list_agents()

    logging.info(agents)

    for enemy_agent in list_agents():
        if enemy_agent == agent_path:
            continue

        print(f"fight {player_id} vs player {enemy_agent}")
        logging.info(f"fight {player_id} vs player {enemy_agent.parent} with {enemy_agent.stem}")

        result = fight_one(agent_path, enemy_agent)

        logging.info(f'result {result}')

        results[f'{player_id}/{agent_path.name}-{enemy_agent.parent.name}/{enemy_agent.name}'] = result

    logging.info(results)

    return results


@app.get("/players")
def read_results():
    with Session(engine) as session:
        statement = select(GameResult)
        results = session.exec(statement).fetchall()
    return results


@app.get("/players/{player_id}")
def read_item(player_id: str, filename: Union[str, None] = None):

    full_agent_path = base_path / Path(player_id) / filename

    logging.info(f'Fight {player_id} with {full_agent_path}')

    results = fight(player_id, full_agent_path)

    with Session(engine) as session:
        for result_enemy, result_value in results.items():
            game_result = GameResult(player=player_id, enemy=result_enemy, result=result_value, created_at=datetime.datetime.now().isoformat())
            session.add(game_result)
        session.commit()

    return {"item_id": player_id, "agent": filename, "result": results}

@app.get("/treasure_hunt")
def treasure_hunt(client_info: str, location: str):

    return {'location': location}
