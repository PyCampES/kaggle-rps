from tournament import run_tournament
from agents.agent_alzheimer import agent_alzheimer
from agents.evil_agent import evil_agent
import kaggle_environments
import json

def print_json(json_):
    print(json.dumps(json_, indent=4))

#run_tournament([agent_alzheimer, evil_agent])

environment = kaggle_environments.make("rps")
logs = environment.run([agent_alzheimer, evil_agent])

print(len(logs))
print_json(logs[-1])



