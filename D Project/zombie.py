from character import Character
from graphics import egi

states = [
    'grouping up',
    'hunting',
    'attacking'
]

class Zombie(Character):
    def __init__(self, world, idx):
        super().__init__(world, idx)
        self.state = states[0]
        self.char_type = 'zombie' # i did this because i can't check types very easily in python :(

    def draw(self):
        egi.red_pen()
        super().draw()

    def set_neighbours_to_hunt(self, done_list):
        # set state to hunting
        self.state = states[1]
        # use recursion to make everyone near you hunting
        for index in self.world.graph.get_neighbours(self.box.idx):
            if index not in done_list:
                guy = self.world.boxes[index].occupant
                if guy is not None:
                    if guy.char_type == 'zombie':
                        done_list.append(self.box.idx)
                        guy.set_neighbours_to_hunt(done_list)

    def update(self):
        # print('box: ', self.box.idx)
        # print('state: ', self.state)

        if self.state == states[0]: # if grouping up
            # AEAEAEAEAEEAEAEAE restrict path limit and if no succesful target then attack nearest human
            zom = self.find_closest_zombie()
            if zom is not None:
                self.calc_path(zom.box.idx, 'AStar', 0) # calculate the path to the closest zombie
            else: self.path = None
            if self.path.path:
                if self.world.boxes[self.path.path[1]].occupant is not None:
                    self.set_neighbours_to_hunt([self.box.idx]) # if the next box is the target then stop moving and change state
                else:
                    self.move_to_box_at_index(self.path.path[1]) # else move to next box

        elif self.state == states[1]:
            hum = self.find_closest_human()
            if hum is not None:
                self.calc_path(hum.box.idx, 'Dijkstra', 0) # calculate path to closest human
            else: self.path = None
            if self.path:
                occupant = self.world.boxes[self.path.path[1]].occupant
                if occupant is not None:
                    if occupant.char_type == 'human':
                        self.state = states[2] # if box has someone in it and they're a human: attack it
                else:
                    self.move_to_box_at_index(self.path.path[1]) # else move to next box

        elif self.state == states[2]:
            human = self.find_closest_human()
            if self.check_human_for_combat(human): # if the human is in a box next to us attack it
                self.am.attack(self, human)
            # either it attacked or it wasn't there for some weird reason so
            self.state = states[1] # set state to group up 

        # else:
        #     # just a precautionary if the variable gets corrupted somehow
        #     self.state = states[1]

    def check_human_for_combat(self, human):
        bool = human.box.idx in self.world.graph.get_neighbours(self.box.idx)
        return bool
