import threading
from character_classes.nuker import Nuker
from clicker import Clicker


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        kind of constructor = get instance
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Launcher(metaclass=Singleton):

    def __init__(self, character_class):
        clicker = Clicker()
        clicker.registerExit(clicker.RIGHT_CTRL, self.stop_event_hendler)

        self.bot_tread_stop_event = threading.Event()

        self.clicker_tread = threading.Thread(target=self.start_clicker, args=(clicker,))
        self.bot_tread = threading.Thread(target=self.start_bot,
                                          args=(clicker, self.bot_tread_stop_event, character_class))

        self.clicker_tread.start()
        self.bot_tread.start()

    @staticmethod
    def start_clicker(clicker):
        clicker.start()

    @staticmethod
    def start_bot(clicker, stop_event, character_class):
        classmap = {
            'Nuker': Nuker,
        }
        bot = classmap[character_class](clicker, stop_event)
        bot.loop()

    def stop_bot(self):
        self.bot_tread_stop_event.set()

    @staticmethod
    def stop_event_hendler(clicker, event):
        print('stop_bot')
        # clicker.stop()
        launcher = Launcher('')
        launcher.stop_bot()

