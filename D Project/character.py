from searches import SEARCHES
from graphics import egi
from attack_manager import Attack_Manager

class Character():
    def __init__(self, world, idx):
        self.world = world
        self.box = None
        self.occupy_box(world.boxes[idx])
        self.power_level = 1
        self.path = None
        self.char_type = ''
        self.am = Attack_Manager(world)

    def draw(self):
        egi.cross(self.box._vc, 7)
        egi.circle(self.box._vc, 10)

    def draw_paths(self):
        if self.path:
            # copied from the box_world

            egi.set_stroke(2)
            # Show open edges
            route = self.path.route
            egi.set_pen_color(name='GREEN')
            for i in self.path.open:
                egi.circle(self.world.boxes[i]._vc, 10)
            # show the partial paths considered
            egi.set_pen_color(name='ORANGE')
            egi.set_stroke(2)
            for i,j in route.items():
                egi.line_by_pos(self.world.boxes[i]._vc, self.world.boxes[j]._vc)
            egi.set_stroke(1)

            # show the final path delivered
            egi.set_pen_color(name='RED')
            egi.set_stroke(2)
            path = self.path.path
            for i in range(1,len(path)):
                egi.line_by_pos(self.world.boxes[path[i-1]]._vc, self.world.boxes[path[i]]._vc)
            egi.set_stroke(1)

    def calc_path(self, target, path_type, limit=50):
        if self.box:
            cls = SEARCHES[path_type]
            self.path = cls(self.world.graph, self.box.idx, target, limit)
        
    def calc_power_level(self):
        indexes = self.world.graph.get_neighbours(self.box.idx)
        power_level = 1
        for index in indexes:
            occupant = self.world.boxes[index].occupant
            if occupant is not None:
                if occupant.char_type == self.char_type:
                    power_level += occupant.power_level
                # might come into a problem here when updating every character
        self.power_level = power_level

    def occupy_box(self, box):
        if self.box:
            self.box.occupant = None
        box.occupant = self
        self.box = box

    def move_to_box_at_index(self, index):
        self.occupy_box(self.world.boxes[index])

    def find_closest_human(self):
        if self.world.humans:
            closest_human = None
            closest_human_distance = None
            for human in self.world.humans:
                if human is self: continue
                if not closest_human:
                    closest_human = human
                    closest_human_distance = self.world._manhattan(self.box.idx, human.box.idx)
                else:
                    new_distance = self.world._manhattan(self.box.idx, human.box.idx)
                    if new_distance < closest_human_distance:
                        closest_human_distance = new_distance
                        closest_human = human
            return closest_human
    
    def find_closest_zombie(self):
        if self.world.zombies:
            closest_zombie = None
            closest_zombie_distance = None
            for zombie in self.world.zombies:
                if zombie is self: continue
                if not closest_zombie:
                    closest_zombie = zombie
                    closest_zombie_distance = self.world._manhattan(self.box.idx, zombie.box.idx)
                else:
                    new_distance = self.world._manhattan(self.box.idx, zombie.box.idx)
                    if new_distance < closest_zombie_distance:
                        closest_zombie_distance = new_distance
                        closest_zombie = zombie

            return closest_zombie

    def check_neighbours(self):
        bool = False
        indexes = self.world.graph.get_neighbours(self.box.idx)
        for index in indexes:
            if self.world.boxes[index].occupant:
                bool = True
                break
        return bool