# kaggle-rps

https://www.kaggle.com/competitions/rock-paper-scissors/

# Jugadas
```python
ROCK = 0
PAPER = 1
SCISSORS = 2
```

# Agent description
Un agente es una función del siguiente estilo:
```python
def agent(observation: dict, configuration: dict) -> int:
    # Your code here
    sign = ROCK
    return sign
```
`observation` es un dict de la siguiente forma: `{'remainingOverageTime': 60, 'step': 0, 'reward': 0, 'lastOpponentAction': 0}`
Donde `step` indica cuántas manos se han jugado y `reward` indica la puntuación hasta el momento (nr. de manos ganadas - nr. de manos perdidas).
`lastOpponentAction` no existe en la primera jugada.

`configuration` es constante: 
```
{'episodeSteps': 30,
 'actTimeout': 1,
 'runTimeout': 1200,
 'signs': 3,
 'tieRewardThreshold': 20,
 'agentTimeout': 60}
```

# Server in Kubernetes (k8s)
- run it in docker-compose
  1. run the rps_carga_agentes
  2. run the tournament runner
  3. create a test for uploading an agent
- add description for uploading

# How to upload your agent?
1. Ensure your python script has a global variable named `agent`, e.g:
```python
def constant_play_agent_1(observation, configuration):
    """Always plays "Paper" (1)"""
    return 1

agent = constant_play_agent_1
```
2. go to <http://192.168.5.172/docs> and use the upload endpoint

# How to run a tournament?
1. go to <http://192.168.5.172:8080/run>

# How to see the result
1. <http://192.168.5.172:8080/>
