# Agent that returns (previousCompetitorStep + shift) % 3
# looks for the same pattern in history and returns the best answer to the most possible counter strategy
class Pattern_Matching(Agent):
    def __init__(self, steps=3, deterministic=False, counter_strategy=False, init_value=0.1, decay=1):
        self.deterministic = deterministic
        self.counter_strategy = counter_strategy
        if counter_strategy:
            self.step_type = 'step'
        else:
            self.step_type = 'competitorStep'
        self.init_value = init_value
        self.decay = decay
        self.steps = steps

    def history_step(self, history):
        if len(history) < self.steps + 1:
            return self.initial_step()

        next_step_count = np.zeros(3) + self.init_value
        pattern = [history[i][self.step_type] for i in range(- self.steps, 0)]

        for i in range(len(history) - self.steps):
            next_step_count = (next_step_count - self.init_value) / self.decay + self.init_value
            current_pattern = [history[j][self.step_type] for j in range(i, i + self.steps)]
            if np.sum([pattern[j] == current_pattern[j] for j in range(self.steps)]) == self.steps:
                next_step_count[history[i + self.steps][self.step_type]] += 1

        if next_step_count.max() == self.init_value:
            return self.initial_step()

        if self.deterministic:
            step = np.argmax(next_step_count)
        else:
            step = np.random.choice([0, 1, 2], p=next_step_count / next_step_count.sum())

        if self.counter_strategy:
            # we predict our step using transition matrix (as competitor can do) and beat probable competitor step
            return (step + 2) % 3
        else:
            # we just predict competitors step and beat it
            return (step + 1) % 3