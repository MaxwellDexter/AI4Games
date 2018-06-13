

class Attack_Manager:
    def __init__(self, world):
        self.world = world

    def attack(self, character_one, character_two):
        character_one.calc_power_level()
        character_two.calc_power_level()

        if character_one.power_level > character_two.power_level:
            # c1 beats c2
            self.kill_character(character_two)
            return True

        elif character_one.power_level < character_two.power_level:
            # c2 beats c1
            self.kill_character(character_one)
            return False

        elif character_one.power_level == character_two.power_level:
            # both c1 and c2 die
            self.kill_character(character_one)
                
            self.kill_character(character_two)
            return False
        
    def kill_character(self, character):
        character.box.occupant = None
        character.box = None
        if character in self.world.humans:
            self.world.humans.remove(character)
        if character in self.world.zombies:
            self.world.zombies.remove(character)
        if character in self.world.characters:
            self.world.characters.remove(character)