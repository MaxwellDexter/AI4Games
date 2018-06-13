class Action():
    def __init__(self, name, goal, preconditions, effects):
        self.name = name
        self.goal = goal
        self.preconditions = preconditions
        self.effects = effects