from bot import Bot
import time
import random


class Nuker(Bot):

    def loop(self):

        while not self.stop_event.is_set():
            if not self.set_next_target():
                areas = self.get_target_areas()
                self.turn(areas.iloc[0].angle)
                self.go(random.randint(20, 25), self.set_next_target)
            self.clean_area(3)

    def self_heal(self, pause=3):
        self_hp = self.self_hp
        if self_hp and self_hp < 70:
            print('self heal')
            self.clicker.press_key(self.clicker.F6, pause)
            self_hp = self.self_hp
            self.clicker.press_key(self.clicker.ESC, 0.2)
            self.set_next_target(0.2)

    def self_heal_decorator(method_to_decorate):

        def wrapper(self, *args, **kwargs):
            self.self_heal()
            return method_to_decorate(self, *args, **kwargs)

        return wrapper

    @Bot.check_state_decorator
    @self_heal_decorator
    def nuke1(self, pause=3):
        print('nuke1')
        self.clicker.press_key(self.clicker.F5, pause)

    @Bot.check_state_decorator
    def kill_mob(self):

        fail_attack_count = 0
        target_hp_0 = self.target_hp
        while target_hp_0:
            self.nuke1(3.5)
            target_hp_1 = self.target_hp
            if target_hp_1 and target_hp_0 and target_hp_1 >= target_hp_0:
                fail_attack_count +=1
                if fail_attack_count==3:
                    return False
            else:
                fail_attack_count = 0
            target_hp_0 = target_hp_1

        if target_hp_0 == 0:
            self.mob_count += 1
            self.last_mob_death_time = time.time()

        return True

    def clean_area(self, step=10):

        class stop_go_somewhere:
            _instances = {}
            nuker = self
            creation_time = time.time()
            def __bool__(self):
                if time.time() > self.__class__.creation_time +30:
                    return True
                else:
                    return self.__class__.nuker.set_next_target()
            def __call__(cls, *args, **kwargs):
                if cls not in cls._instances:
                    cls._instances[cls] = super(stop_go_somewhere, cls).__call__(*args, **kwargs)
                return cls._instances[cls]

        for i in range(step):
            stop_go_somewhere.creation_time = time.time()
            while not self.stop_event.is_set() and self.set_next_target():
                if not self.kill_mob():
                    self.clicker.press_key(self.clicker.ESC,0.2)
                    self.go_somewhere(12)
                if self.go_to_selected_target():
                    self.pick_up_drop()
                    self.sweep()
                self.self_heal()
            self.go_somewhere(stop_event=stop_go_somewhere)



