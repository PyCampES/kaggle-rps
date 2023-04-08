from itertools import combinations

import kaggle_environments


def run_tournament(list_of_agents):
    """Runs a rock, paper, scissors tournament given a list of agents.

    Agents need to be functions that return a number representing a rock (0),
    paper(1) or scissors (2).

    """
    if not list_of_agents:
        print("No agents were provided.")
        return

    # Create all matches from all possible combinations of agents
    matches = combinations(list_of_agents, r=2)

    for (agent_A, agent_B) in matches:
        print(f"\n\n=== {agent_A.__name__} VS {agent_B.__name__} ===")

        is_match_finished = False
        while not is_match_finished:
            environment = kaggle_environments.make("rps")
            match_data = environment.run([agent_A, agent_B])

            # Compute the score of the agents
            score_A, score_B = [
                    match_data[-1][id_agent]["reward"]
                    for id_agent in range(2)
            ]

            # Check if agent A is the winner
            if score_A > score_B:
                is_match_finished = True
                print(f"{agent_A.__name__} wins with {score_A} points")

            # Check if agent B is the winner
            if score_A < score_B:
                is_match_finished = True
                print(f"{agent_B.__name__} wins with {score_B} points")

        print("\n\n")
