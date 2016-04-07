from ctypes import c_int, POINTER, c_void_p, addressof, ArgumentError
from libtoxcore import LibToxCore
from toxav_enums import *


class ToxAV(object):
    """
    The ToxAV instance type. Each ToxAV instance can be bound to only one Tox instance, and Tox instance can have only
    one ToxAV instance. One must make sure to close ToxAV instance prior closing Tox instance otherwise undefined
    behaviour occurs. Upon closing of ToxAV instance, all active calls will be forcibly terminated without notifying
    peers.
    """

    libtoxcore = LibToxCore()

    # -----------------------------------------------------------------------------------------------------------------
    # Creation and destruction
    # -----------------------------------------------------------------------------------------------------------------

    def __init__(self, tox_pointer):
        """
        Start new A/V session. There can only be only one session per Tox instance.

        :param tox_pointer: pointer to Tox instance
        """
        toxav_err_new = c_int()
        ToxAV.libtoxcore.toxav_new.restype = POINTER(c_void_p)
        self._toxav_pointer = ToxAV.libtoxcore.toxav_new(tox_pointer, addressof(toxav_err_new))
        toxav_err_new = toxav_err_new.value
        if toxav_err_new == TOXAV_ERR_NEW['NULL']:
            raise ArgumentError('One of the arguments to the function was NULL when it was not expected.')
        elif toxav_err_new == TOXAV_ERR_NEW['MALLOC']:
            raise MemoryError('Memory allocation failure while trying to allocate structures required for the A/V '
                              'session.')
        elif toxav_err_new == TOXAV_ERR_NEW['MULTIPLE']:
            raise RuntimeError('Attempted to create a second session for the same Tox instance.')

    def __del__(self):
        """
        Releases all resources associated with the A/V session.

        If any calls were ongoing, these will be forcibly terminated without notifying peers. After calling this
        function, no other functions may be called and the av pointer becomes invalid.
        """
        ToxAV.libtoxcore.toxav_kill(self._toxav_pointer)

    def get_tox_pointer(self):
        """
        Returns the Tox instance the A/V object was created for.

        :return: pointer to the Tox instance
        """
        ToxAV.libtoxcore.toxav_get_tox.restype = POINTER(c_void_p)
        return ToxAV.libtoxcore.toxav_get_tox(self._toxav_pointer)

    # -----------------------------------------------------------------------------------------------------------------
    # TODO A/V event loop
    # -----------------------------------------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------------------------------------
    # TODO Call setup
    # -----------------------------------------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------------------------------------
    # TODO Call state graph
    # -----------------------------------------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------------------------------------
    # TODO Call control
    # -----------------------------------------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------------------------------------
    # TODO Controlling bit rates
    # -----------------------------------------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------------------------------------
    # TODO A/V sending
    # -----------------------------------------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------------------------------------
    # TODO A/V receiving
    # -----------------------------------------------------------------------------------------------------------------
