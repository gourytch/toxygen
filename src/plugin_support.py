import util
import profile
import os
import imp
import inspect
import plugins.plugin_super_class as pl


class PluginLoader(util.Singleton):

    def __init__(self, tox, settings):
        self._profile = profile.Profile.get_instance()
        self._settings = settings
        self._plugins = {}  # dict. key - plugin unique short name, value - tuple (plugin instance, is active)
        self._tox = tox

    def load(self):
        """
        Load all plugins in plugins folder
        """
        path = util.curr_directory() + '/plugins/'
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        for fl in files:
            if fl in ('plugin_super_class.py', '__init__.py') or not fl.endswith('.py'):
                continue
            name = fl[:-3] # module name without .py
            try:
                module = imp.load_source('plugins.' + name, path + fl)  # import plugin
            except ImportError:
                util.log('Import error in module ' + name)
                continue
            except Exception as ex:
                util.log('Exception in module ' + name + ' Exception: ' + str(ex))
                continue
            for elem in dir(module):
                obj = getattr(module, elem)
                if inspect.isclass(obj) and issubclass(obj, pl.PluginSuperClass):  # looking for plugin class in module
                    print elem
                    try:  # create instance of plugin class
                        inst = obj(self._tox, self._profile, self._settings)
                        autostart = inst.get_short_name() in self._settings['plugins']
                        if autostart:
                            inst.start()
                    except Exception as ex:
                        util.log('Exception in module ' + name + ' Exception: ' + str(ex))
                        continue
                    self._plugins[inst.get_short_name()] = [inst, autostart]  # (inst, is active)
                    break

    def callback_custom_packet(self, is_lossless=True):
        """
        New incoming custom packet (callback)
        """
        def wrapped(tox, friend_number, data, length, user_data):
            l = data[0] - pl.LOSSLESS_FIRST_BYTE if is_lossless else data[0] - pl.LOSSY_FIRST_BYTE
            name = ''.join(chr(x) for x in data[1:l + 1])
            print name
            if name in self._plugins:
                if is_lossless:
                    self._plugins[name][0].lossless_packet(''.join(chr(x) for x in data[l + 1:length]), friend_number)
                else:
                    self._plugins[name][0].lossy_packet(''.join(chr(x) for x in data[l + 1:length]), friend_number)
        return wrapped

    def get_plugins_list(self):
        """
        Returns list of all plugins
        """
        result = []
        for key in self._plugins:
            data = self._plugins[key]
            print data[0]
            result.append([data[0].get_name(),
                           data[1],
                           data[0].get_description(),
                           data[0].get_short_name()])
        return result

    def plugin_window(self, key):
        return self._plugins[key][0].window()

    def toggle_plugin(self, key):
        """
        Enable/disable plugin
        :param key: plugin short name
        """
        plugin = self._plugins[key]
        if plugin[1]:
            plugin[0].stop()
        else:
            plugin[0].start()
        plugin[1] = not plugin[1]
        if plugin[1]:
            self._settings['plugins'].append(key)
        else:
            self._settings['plugins'].remove(key)
        self._settings.save()

    def command(self, text):
        text = text.strip()
        name = text.split()[0]
        if name in self._plugins:
            self._plugins[name][0].command(text[len(name) + 1:])
