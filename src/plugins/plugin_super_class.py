import os
from PySide import QtCore, QtGui


MAX_SHORT_NAME_LENGTH = 5

LOSSY_FIRST_BYTE = 200

LOSSLESS_FIRST_BYTE = 160


def path_to_data(name):
    return os.path.dirname(os.path.realpath(__file__)) + '/' + name + '/'


class PluginSuperClass(object):
    """
    Superclass for all plugins. Plugin is python module. This module must contain
    at least 1 class derived from this class.
    """

    def __init__(self, name, short_name, tox=None, profile=None, settings=None):
        """
        :param name: plugin full name
        :param short_name: plugin unique short name (length of short name should not exceed MAX_SHORT_NAME_LENGTH)
        :param tox: tox instance
        :param profile: profile instance
        :param settings: profile settings
        """
        self._settings = settings
        self._profile = profile
        self._tox = tox
        name = name.strip()
        short_name = short_name.strip()
        if not name or not short_name:
            raise NameError('Wrong name')
        self._name = name
        self._short_name = short_name[:MAX_SHORT_NAME_LENGTH]
        self._translator = None

    def get_name(self):
        """
        :return plugin full name
        """
        return self._name

    def get_short_name(self):
        """
        :return plugin unique (short) name
        """
        return self._short_name

    def set_tox(self, tox):
        """
        New tox instance
        """
        self._tox = tox

    def start(self):
        """
        This method called when plugin was started
        """
        pass

    def stop(self):
        """
        This method called when plugin was stopped
        """
        pass

    def command(self, command):
        """
        New command.
        :param command: string with command
        """
        pass

    def get_description(self):
        """
        Return plugin description
        """
        return self.__doc__

    def window(self):
        """
        This method should return window for plugins with GUi or None
        """
        return None

    def load_translator(self):
        """
        This method loads translations for GUI
        """
        app = QtGui.QApplication.instance()
        langs = self._settings.supported_languages()
        curr_lang = self._settings['language']
        if curr_lang in map(lambda x: x[0], langs):
            if self._translator is not None:
                app.removeTranslator(self._translator)
            self._translator = QtCore.QTranslator()
            lang_path = filter(lambda x: x[0] == curr_lang, langs)[0][1]
            self._translator.load(path_to_data(self._short_name) + lang_path)
            app.installTranslator(self._translator)

    def load_settings(self):
        """
        This method loads settings of plugin and returns raw data
        """
        with open(path_to_data(self._short_name + 'settings.json')) as fl:
            data = fl.read()
        return data

    def save_settings(self, data):
        """
        This method saves plugin's settings to file
        :param data: string with data
        """
        with open(path_to_data(self._short_name + 'settings.json')) as fl:
            fl.write(data)

    def lossless_packet(self, data, friend_number):
        """
        Incoming lossless packet
        :param data: raw data
        :param friend_number: number of friend who sent packet
        """
        pass

    def lossy_packet(self, data, friend_number):
        """
        Incoming lossy packet
        :param data: raw data
        :param friend_number: number of friend who sent packet
        """
        pass

    def send_lossless(self, data, friend_number):
        """
        This method sends lossless packet to friend
        Wrapper for self._tox.friend_send_lossless_packet
        """
        self._tox.friend_send_lossless_packet(friend_number, chr(len(self._short_name) + LOSSLESS_FIRST_BYTE) +
                                              self._short_name + str(data))

    def send_lossy(self, data, friend_number):
        """
        This method sends lossy packet to friend
        Wrapper for self._tox.friend_send_lossy_packet
        """
        self._tox.friend_send_lossy_packet(friend_number, chr(len(self._short_name) + LOSSY_FIRST_BYTE) +
                                           self._short_name + str(data))
