from character import Character
from graphics import egi
import copy
from action import Action
from searches import SEARCHES
import random
from collections import OrderedDict

class Human(Character):
    def __init__(self, world, idx):
        super().__init__(world, idx)
        self.char_type = 'human'

        self.action_plan = []
        self.goals = [
            'kill zombies in area',
            'flee from zombies',
            'recuperate',
            'increase utility'
            # maybe hunger?
        ]
        self.actions = [
            Action('group up', 'kill zombies in area', None, {'stamina': -2}),
            Action('attack', 'kill zombies in area', None, {'stamina': -4}),
            Action('run away', 'flee from zombies', None, {'stamina': -1}),
            Action('rest', 'recuperate', None, {'stamina': 5}),
            Action('scan zombie', 'increase utility', None, {'stamina': 1, 'scanned': True}),
            Action('scan human', 'increase utility', None, {'stamina': 1, 'scanned': True}),
            Action('wander', 'increase utility', None, {'stamina': -1})
        ]
        self.attributes = {
            'stamina': 15,
            'scanned': False
            # could have a flare gun thing
        }

    def draw(self):
        egi.blue_pen()
        super().draw()
        

    def update(self):
        # super().calc_path(30, 'Dijkstra')
        if not self.action_plan:
            self.plan_actions_rb()
        # print('*'*10)
        # print('Box: ', self.box.idx)
        # print('stamina: ', self.attributes['stamina'])
        # for action in self.action_plan:
        #     print('Action: ', action.name)
        self.execute_plan()

# ===============================================================
# executing plan
# ===============================================================

    def execute_plan(self):
        # print('+'*40)
        action = self.action_plan.pop(0)
        # for action in self.action_plan:
        if self.check_replan(action):
            # print('REPLANNING')
            # time for a replan
            self.action_plan = []
            self.attributes['stamina'] += 1
        else:
            if action.name == 'group up':
                self.group_up()
            elif action.name == 'attack':
                self.attack()
            elif action.name == 'run away':
                self.run_away()
            elif action.name == 'rest':
                self.rest()
                self.attributes['stamina'] += self.actions[3].effects['stamina']
            elif action.name == 'scan zombie':
                self.scan_for_zombie()
                self.attributes['stamina'] += self.actions[4].effects['stamina']
            elif action.name == 'scan human':
                self.scan_for_human()
                self.attributes['stamina'] += self.actions[5].effects['stamina']
            elif action.name == 'wander':
                self.wander()
                self.attributes['stamina'] += self.actions[6].effects['stamina']

            if action != 'scan zombie' or action != 'scan human':
                self.scanned = False
            # have to remove head

    def check_replan(self, action):
        if self.attributes['stamina'] + action.effects['stamina'] < 0:
            return True # about checking if zombies nearby and attack
        if action.name == 'rest' and self.attributes['stamina'] + action.effects['stamina'] > 15:
            return True
        if self.actions[1].name in self.action_plan and not self.find_nearby_zombies(self.get_boxes_in_radius_bfs(25, self.box.idx)):
            print('&'*100)
            return True
        else:
            return False

    def group_up(self):
        hum = self.find_closest_human()
        if self.attributes['scanned']:
            self.attributes['scanned'] = False
            # this makes sure that the efforts of a scan are not overridden 
        else:
            if hum is not None:
                self.calc_path(hum.box.idx, 'AStar')
            else: self.path = None
        if self.path:
            if len(self.path.path) > 1:
                if self.world.boxes[self.path.path[1]].occupant is None:
                    self.move_to_box_at_index(self.path.path[1]) #  move to next box
                    self.attributes['stamina'] += self.actions[0].effects['stamina']
        else:
            print('no guy nearby')
            # time for replan

    def attack(self):
        zombie = self.find_closest_zombie()
        if zombie is not None:
            self.calc_path(zombie.box.idx, 'Dijkstra', 0)
        else: self.path = None
        if self.path:
            occupant = self.world.boxes[self.path.path[1]].occupant
            if occupant is not None:
                if occupant.char_type == 'zombie':
                    self.am.attack(self, zombie)
                    self.attributes['stamina'] += self.actions[1].effects['stamina']
            else:
                self.move_to_box_at_index(self.path.path[1]) # else move to next box
                self.attributes['stamina'] += self.actions[0].effects['stamina']

    def check_zombie_for_combat(self, zombie):
        bool = zombie.box.idx in self.world.graph.get_neighbours(self.box.idx)
        return bool

    def run_away(self):
        idxs = self.calc_influence_map()
        # print('#'*40)
        # print(idxs)
        # print('len: ', len(idxs))
        # egi.red_pen
        # for i in idxs:
        #     egi.cross(self.world.boxes[i]._vc, 10)
        safe_box = self.find_safe_box(idxs)
        # print('safe: ', safe_box)
        if safe_box is not None:
            self.calc_path(safe_box, 'AStar')
            if self.path.path:
                # print('path: ', self.path.path)
                # print('box: ', self.world.boxes[self.path.path[1]].idx)
                if len(self.path.path) > 1:
                    if self.world.boxes[self.path.path[1]].occupant is None:
                        self.move_to_box_at_index(self.path.path[1]) # else move to next box
                        self.attributes['stamina'] += self.actions[2].effects['stamina']
        else:
            self.wander()

    '''
    def find_closest_safe_box(self, box_map):
        # very expensive!
        best_distance = 0
        best_index = None
        cls = SEARCHES['AStar']
        for idx in box_map:
            temp_distance = cls(self.world.graph, self.box.idx, idx).steps
            if best_index is None:
                best_index = idx
                best_distance = temp_distance
            elif temp_distance < best_distance:
                best_index = idx
                best_distance = temp_distance
        return best_index
    '''

    def find_safe_box(self, box_map):
        box_queue = [self.box.idx]
        # while box_queue:
        for i in range(25):
            head = box_queue[0]
            box_queue.pop(0)
            for neighbour in self.world.graph.get_neighbours(head):
                if neighbour in box_map:
                    return neighbour
                box_queue.append(neighbour)
        return None

    def calc_influence_map(self):
        zombie_index_map = []
        for zombie in self.world.zombies:
            zombie_index_map += self.get_boxes_in_radius_bfs(25, zombie.box.idx)

        # print(len(zombie_index_map))
        zombie_index_map = list(set(zombie_index_map)) # removing duplicates
        # print(len(zombie_index_map))
        world_indexes = []
        for box in self.world.boxes:
            world_indexes.append(box.idx)
        safe_boxes = [n for n in world_indexes if n not in zombie_index_map]
        return list(set(safe_boxes))

    def rest(self):
        # maybe rest could increase the vision temporarily
        # print('resting')
        sss = 1

    def scan_for_human(self):
        # self.scanned = True
        if self.world.humans:
            self.path = self.calc_path(self.find_closest_human().box.idx, 'Dijkstra', 100)
            self.attributes['scanned'] = True
        # print('scanning')
        # self.get_boxes_in_radius_bfs(100)

    def scan_for_zombie(self):
        # self.scanned = True
        if self.world.zombies:
            self.path = self.calc_path(self.find_closest_zombie().box.idx, 'Dijkstra', 100)
            self.attributes['scanned'] = True
        # print('scanning')

    def wander(self):
        indexes = self.world.graph.get_neighbours(self.box.idx)
        # check neighbours for occupants
        to_remove = []
        for i in indexes:
            if self.world.boxes[i].occupant is not None:
                to_remove.append(i)
        for i in to_remove:
            indexes.remove(i)
        if indexes:
            self.calc_path(random.choice(indexes), 'AStar')
        if self.path:
            if self.world.boxes[self.path.path[1]].occupant is None:
                self.move_to_box_at_index(self.path.path[1])


# ***************************************************************
# end execution of plan
# ***************************************************************


# ===============================================================
# planning
# ===============================================================
    

    def plan_actions_rb(self):
        boxes_indexes = self.get_boxes_in_radius_bfs(25, self.box.idx)
        # for i in boxes_indexes:
        #     egi.cross(self.world.boxes[i]._vc, 10)
        characters_index = self.find_nearby_characters(boxes_indexes)
        best_plan = []
        best_contentment = None
        attributes_copy = copy.deepcopy(self.attributes)
        for goal in self.goals:
            temp_plan, temp_contentment = self.plan_rule_based(goal, characters_index, copy.deepcopy(self.attributes))
            if best_contentment is None:
                best_plan = temp_plan
                best_contentment = temp_contentment
            elif temp_contentment > best_contentment:
                best_plan = temp_plan
                best_contentment = temp_contentment
        self.action_plan = best_plan

    def plan_rule_based(self, goal, character_indexes, attributes):
        plan = []
        contentment = 0
        for action in self.actions:
            temp_contentment = 0
            if action.goal == goal:

                self.calc_power_level()
                zombies_nearby = []
                humans_nearby = []
                for character in character_indexes:
                    if self.world.boxes[character].occupant.char_type == 'zombie':
                        zombies_nearby.append(character)
                    elif self.world.boxes[character].occupant.char_type == 'human':
                        humans_nearby.append(character)
                
                if goal == 'recuperate':
                    if action.name == 'rest':
                        if zombies_nearby or attributes['stamina'] > 9:
                            temp_contentment -= 100
                            plan.append(action)
                        else:
                            temp_contentment += 3
                            plan.append(action)

                elif goal == 'kill zombies in area':
                    if not zombies_nearby:
                        temp_contentment -= 5
                        plan.append(action)
                    elif action.name == 'group up':
                        if humans_nearby:
                            temp_contentment += 10
                            cls = SEARCHES['AStar']
                            path = cls(self.world.graph, self.box.idx, humans_nearby[0])
                            for step in range(path.steps):
                                temp_contentment += action.effects['stamina']
                                plan.append(action)
                        else:
                            plan.append(action)
                            temp_contentment -= 5
                    elif action.name == 'attack':
                        plan.append(action)
                        for zom in zombies_nearby:
                            self.world.boxes[zom].occupant.calc_power_level()
                            if self.world.boxes[zom].occupant.power_level > self.power_level:
                                temp_contentment -= self.world.boxes[zom].occupant.power_level - self.power_level
                            else:
                                temp_contentment += self.power_level - self.world.boxes[zom].occupant.power_level

                elif goal == 'flee from zombies':
                    if action.name == 'run away':
                        if zombies_nearby:
                            if humans_nearby:
                                num = (len(zombies_nearby) - (len(humans_nearby) + 1)) * 2
                                temp_contentment += num
                                if num > 1:
                                    for i in range(num):
                                        plan.append(action)
                                else:
                                    plan.append(action)
                            else:
                                for zom in zombies_nearby:
                                    temp_contentment += 5
                                    plan.append(action)
                                    plan.append(action)
                        else:
                            temp_contentment -= 5
                            plan.append(action)

                elif goal == 'increase utility':
                    if action.name == 'scan zombie' or action.name == 'scan human':
                        plan.append(action)
                        if attributes['scanned'] is False and not zombies_nearby:
                            temp_contentment += 5
                        else:
                            temp_contentment -= 5
                    elif action.name == 'wander':
                        if not zombies_nearby and not humans_nearby and attributes['stamina'] > 9:
                            for i in range(4):
                                plan.append(action)
                            temp_contentment += 20
                        else:
                            plan.append(action)
                            temp_contentment += 2

                temp_contentment += action.effects['stamina']

                attributes = self.update_attributes(action, attributes)
                contentment += temp_contentment

        return (plan, contentment)

    def update_attributes(self, action, attributes):
        for effect_key, effect_value in action.effects.items():
            for attribute_key, attribute_value in attributes.items():
                if effect_key == 'stamina' and attribute_key == 'stamina':
                    attributes['stamina'] += effect_value
                if effect_key == 'scanned' and attribute_key == 'scanned':
                    attributes['scanned'] = effect_value
        return attributes

    def find_nearby_characters(self, indexes):
        boxes_with_occupants = []
        for index in indexes:
            if self.world.boxes[index].occupant is not None:
                boxes_with_occupants.append(index)
        return boxes_with_occupants

    def find_nearby_zombies(self, indexes):
        boxes_with_occupants = []
        for index in indexes:
            if self.world.boxes[index].occupant is not None:
                if self.world.boxes[index].occupant.char_type == 'zombie':
                    boxes_with_occupants.append(index)
        return boxes_with_occupants

    def get_boxes_in_radius_bfs(self, radius, original_box):
        box_queue = [original_box]
        nearby = []
        # while box_queue:
        for i in range(radius):
            head = box_queue[0]
            box_queue.pop(0)
            for neighbour in self.world.graph.get_neighbours(head):
                if neighbour not in nearby:
                    nearby.append(neighbour)
                    if neighbour not in box_queue:
                        box_queue.append(neighbour)
        if original_box == self.box.idx:
            nearby.remove(original_box)
        return nearby



# can use target index

# ***************************************************************
# end planning
# ***************************************************************


'''
    def check_preconditions(self, action, attributes):
        if action.preconditions is None:
            return True
        precon_met = []
        for precondition_key, precondition_value in action.preconditions.items():
            for attribute_key, attribute_value in attributes.items():
                if attribute_key == precondition_key:
                    if attribute_value is precondition_value:
                        precon_met.append(True)
                    else:
                        precon_met.append(False)
        if precon_met is None:
            return True
        elif False in precon_met:
            return False
        else:
            return True
    
    def plan_actions_again(self):

        boxes_indexes = self.get_boxes_in_radius_bfs(25, self.box.idx)
        # for i in boxes_indexes:
        #     egi.cross(self.world.boxes[i]._vc, 10)
        characters_index = self.find_nearby_characters(boxes_indexes)

        best_plan = []
        best_disc = None
        attributes_copy = copy.deepcopy(self.attributes)
        for goal in self.goals:
            temp_plan, temp_disc = self.plan(goal, characters_index, attributes_copy)
            # temp_plan = self.find_actions(goal, attributes_copy, temp_plan, True, action)
            if best_disc is None:
                best_plan = temp_plan
                best_disc = temp_disc
            elif temp_disc < best_disc:
                best_plan = temp_plan
                best_disc = temp_disc
        self.action_plan = best_plan

    def plan(self, goal, character_indexes, attributes):
        plan = []
        discontentment = 0
        for action in self.actions:
            temp_discontentment = 0
            if action.goal == goal:

                self.calc_power_level()
                zombies_nearby = []
                humans_nearby = []
                for character in character_indexes:
                    if self.world.boxes[character].occupant.char_type == 'zombie':
                        zombies_nearby.append(character)
                    elif self.world.boxes[character].occupant.char_type == 'human':
                        humans_nearby.append(character)

                if goal == 'recuperate' or goal == 'increase utility':
                    temp_discontentment = (len(zombies_nearby) - len(humans_nearby)) * 2
                elif goal == 'kill zombies in area':
                    if action.name == 'attack':
                        temp_discontentment = len(zombies_nearby) - (self.power_level + len(humans_nearby))
                    elif action.name == 'group up':
                        if not humans_nearby:
                            temp_discontentment = 20
                        else:
                            temp_discontentment = len(zombies_nearby) - len(humans_nearby)
                elif goal == 'flee from zombies':
                    if zombies_nearby:
                        temp_discontentment = 0
                    else:
                        temp_discontentment = 20

                if action.name == 'group up' and humans_nearby:
                    cls = SEARCHES['AStar']
                    path = cls(self.world.graph, self.box.idx, humans_nearby[0])
                    for step in path.steps:
                        plan.append(action)
                        discontentment += self.calc_disc_with_stamina(attributes['stamina'], action.effects['stamina'], temp_discontentment)
                elif action.name == 'rest' and attributes['stamina'] >= 10:
                    temp_discontentment += 20
                    plan.append(action)
                elif action.name == 'scan for zombie' or action.name == 'scan for human' and attributes['scanned'] is True:
                    temp_discontentment += 20
                    plan.append(action)
                else:
                    plan.append(action)
                    discontentment += self.calc_disc_with_stamina(attributes['stamina'], action.effects['stamina'], temp_discontentment)


                # for effect_key, effect_value in action.effects.items():
                #     for attribute_key, attribute_value in attributes.items():
                #         if effect_key == 'stamina' and attribute_key == 'stamina':
                #             attributes['stamina'] +=

        return (plan, discontentment)
        
    def calculate_action_plan(self, goal, character_indexes, action, attributes):
        action_queue = [action]
        # bfs here
        action_list = []
        for action in self.actions:
            if action.goal == goal:
                action_list.append(action)

        plan = []

        zombies_nearby = []
        humans_nearby = []
        self.calc_power_level()
        for character in character_indexes:
            if world.boxes[character].occupant.char_type == 'zombie':
                zombies_nearby.append(character)
            elif world.boxes[character].occupant.char_type == 'human':
                humans_nearby.append(character)
        # if zombies_nearby and self.calc_power_level < 2:
        #     actions_discontentment['attack'] = 20
        if zombies_nearby and self.power_level > 1:
            lowest_discontentment = 0
            for zom in zombies_nearby:
                world.boxes[zom].occupant.calc_power_level()
                if world.boxes[zom].occupant.power_level - self.power_level < lowest_discontentment:
                    lowest_discontentment = -(world.boxes[zom].occupant.power_level - self.power_level)
                    # actions_discontentment['attack'] = -(world.boxes[zom].occupant.power_level - self.power_level)
                # elif world.boxes[zom].occupant.power_level - self.power_level > 0:
                    # actions_discontentment['run away'] += world.boxes[zom].occupant.power_level - self.power_level
        if humans_nearby:
            for human in humans_nearby:

        # elif not zombies_nearby:


        # group up action should count the steps and for add that to list
        for i in range(5):
            actions_discontentment = []
            for for action in self.actions:
                actions_discontentment.append()
            while action_queue:
                head = action_queue[0]
                head_discontentment = 0
                action_queue.pop(0)
                for action in self.actions:
                    if self.check_preconditions(action, attributes):
                        action_queue.append(action)

                # do stuff with head
                if attributes['stamina'] + head.effects['stamina'] < 0 or attributes['stamina'] + head.effects['stamina'] > 15:
                    head_discontentment = 50

                

                
        
        return action_list

    def find_actions(self, goal, temp_attributes, action_list, is_root, root_action):
        if is_root:
            if root_action.goal is goal:
                if root_action.preconditions is None or self.check_preconditions(root_action, temp_attributes):
                    action_list = [root_action]
                    if goal in root_action.effects:
                        return action_list
                    temp_attributes = self.apply_actions(root_action, temp_attributes)
                    action_list = self.find_actions(goal, temp_attributes, action_list, False, root_action)
                    return action_list
        else:
            # could use recursion
            for action in self.actions:
                if action.goal is goal:
                    if action.preconditions is None or self.check_preconditions(action, temp_attributes):
                        if goal in action.effects:
                            action_list.append(action)
                            return action_list
                        # if effects affect anything
                        for effect_key, effect_value in action.effects.items():
                            for attribute_key, attribute_value in temp_attributes.items():
                                if effect_key == attribute_key and attribute_value is not effect_value:
                                    action_list.append(action)
                                    temp_attributes = self.apply_actions(action, temp_attributes)
                                    action_list = self.find_actions(goal, temp_attributes, action_list, False, root_action)
                                    return action_list

    def apply_actions(self, action, temp_attributes):
        new_attributes = {}
        for attribute_key, attribute_value in temp_attributes.items():
            for effect_key, effect_value in action.effects.items():
                if effect_key is attribute_key:
                    if attribute_key is 'stamina' and effect_key is 'stamina':
                        attribute_value += effect_value
                    else:
                        attribute_value = effect_value
            if attribute_key not in new_attributes:
                new_attributes[attribute_key] = attribute_value
        return new_attributes

    def calculate_discontentment(self, action_list):
        result = 0
        if action_list:
            for action in action_list:
                if 'stamina' in action.effects:
                    result -= action.effects['stamina']
        else:
            return 1000
        return result


    def plan_actions(self):
        boxes_indexes = self.get_boxes_in_radius_bfs(25)
        for i in boxes_indexes:
            egi.cross(self.world.boxes[i]._vc, 10)
        characters_index = self.find_nearby_characters(boxes_indexes)
        cost = None
        best_plan = []
        best_disc = None
        temp_plan = []
        for action in self.actions:
            temp_plan = self.find_actions(goal, attributes_copy, temp_plan, True, action)
            new_cost = self.calculate_cost(temp_plan)
            new_disc = self.calculate_discontentment(temp_plan)
            if cost is None:
                cost = new_cost
                best_plan = temp_plan
                best_disc = new_disc
            elif new_cost < cost:
                cost = new_cost
                best_plan = temp_plan
                best_disc = new_disc
            elif new_cost == cost:
                if new_disc < best_disc:
                    # cost is already new_cost
                    best_plan = temp_plan
                    best_disc = new_disc
        self.action_plan = best_plan


    def gather_action_plans(self, character_indexes, discontentment, action_plan):
        best_plan = {}
        for action in self.actions:
            action_dis = self.calculate_action_plan(character_indexes, action)
            if best_plan is None:
                best_plan = action_dis
            elif action_dis[action_dis.keys()[0]] < best_plan[best_plan.keys()[0]]:
                best_plan = action_dis
        return best_plan

    

    def find_actions(self, action, character_indexes):
        world = self.world.copy()
        actions_discontentment = {
            'group up' : 0,
            'attack' : 0,
            'run away' : 0,
            'rest' : 0,
            'scan zombie' : 0,
            'scan human' : 0
        }
        zombies_nearby = []
        humans_nearby = []
        self.calc_power_level()
        for character in character_indexes:
            if world.boxes[character].occupant.char_type == 'zombie':
                zombies_nearby.append(character)
            elif world.boxes[character].occupant.char_type == 'human':
                humans_nearby.append(character)
        if zombies_nearby and self.calc_power_level < 2:
            actions_discontentment['attack'] = 20
        elif zombies_nearby and self.calc_power_level > 1:
            lowest_discontentment = 0
            for zom in zombies_nearby:
                world.boxes[zom].occupant.calc_power_level()
                if world.boxes[zom].occupant.power_level - self.power_level < lowest_discontentment:
                    lowest_discontentment = -(world.boxes[zom].occupant.power_level - self.power_level)
                    actions_discontentment['attack'] = -(world.boxes[zom].occupant.power_level - self.power_level)
                elif world.boxes[zom].occupant.power_level - self.power_level > 0:
                    actions_discontentment['run away'] += world.boxes[zom].occupant.power_level - self.power_level
        if humans_nearby:
            for human in humans_nearby:

        elif not zombies_nearby:
        '''