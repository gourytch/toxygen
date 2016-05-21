import os


MAX_SHORT_NAME_LENGTH = 5

LOSSY_FIRST_BYTE = 200

LOSSLESS_FIRST_BYTE = 160


def path_to_data(name):
    return os.path.dirname(os.path.realpath(__file__)) + '/' + name + '/settings.json'


class PluginSuperClass(object):

    def __init__(self, name, short_name, tox=None, profile=None, settings=None):
        self._settings = settings
        self._profile = profile
        self._tox = tox
        name = name.strip()
        short_name = short_name.strip()
        if not name or not short_name:
            raise NameError('Wrong name or short name')
        self._name = name
        self._short_name = short_name[:MAX_SHORT_NAME_LENGTH]

    def get_name(self):
        return self._name

    def get_short_name(self):
        return self._short_name

    def start(self):
        pass

    def stop(self):
        pass

    def get_description(self):
        return self.__doc__

    def window(self):
        return None

    def load_settings(self):
        with open(path_to_data(self._short_name)) as fl:
            data = fl.read()
        return data

    def save_settings(self, data):
        with open(path_to_data(self._short_name)) as fl:
            fl.write(data)

    def lossless_packet(self, data, friend_number):
        pass

    def lossy_packet(self, data, friend_number):
        pass

    def send_lossless(self, data, friend_number):
        self._tox.friend_send_lossless_packet(friend_number, chr(len(self._short_name) + LOSSLESS_FIRST_BYTE) +
                                              self._short_name + str(data))

    def send_lossy(self, data, friend_number):
        self._tox.friend_send_lossy_packet(friend_number, chr(len(self._short_name) + LOSSY_FIRST_BYTE) +
                                           self._short_name + str(data))
