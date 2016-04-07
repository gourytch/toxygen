from ctypes import c_int, POINTER, c_void_p, addressof, ArgumentError, c_uint32
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
    # A/V event loop
    # -----------------------------------------------------------------------------------------------------------------

    def iteration_interval(self):
        """
        Returns the interval in milliseconds when the next toxav_iterate call should be. If no call is active at the
        moment, this function returns 200.

        :return: interval in milliseconds
        """
        return ToxAV.libtoxcore.toxav_iteration_interval(self._toxav_pointer)

    def iterate(self):
        """
        Main loop for the session. This function needs to be called in intervals of toxav_iteration_interval()
        milliseconds. It is best called in the separate thread from tox_iterate.
        """
        ToxAV.libtoxcore.toxav_iterate(self._toxav_pointer)

    # -----------------------------------------------------------------------------------------------------------------
    # TODO Call setup
    # -----------------------------------------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------------------------------------
    # TODO Call state graph
    # -----------------------------------------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------------------------------------
    # Call control
    # -----------------------------------------------------------------------------------------------------------------

    def call_control(self, friend_number, control):
        """
        Sends a call control command to a friend.

        :param friend_number: The friend number of the friend this client is in a call with.
        :param control: The control command to send.
        :return: True on success.
        """
        toxav_err_call_control = c_int()
        result = ToxAV.libtoxcore.toxav_call_control(self._toxav_pointer, c_uint32(friend_number), c_int(control),
                                                     addressof(toxav_err_call_control))
        toxav_err_call_control = toxav_err_call_control.value
        if toxav_err_call_control == TOXAV_ERR_CALL_CONTROL['OK']:
            return bool(result)
        elif toxav_err_call_control == TOXAV_ERR_CALL_CONTROL['SYNC']:
            raise RuntimeError('Synchronization error occurred.')
        elif toxav_err_call_control == TOXAV_ERR_CALL_CONTROL['FRIEND_NOT_FOUND']:
            raise ArgumentError('The friend_number passed did not designate a valid friend.')
        elif toxav_err_call_control == TOXAV_ERR_CALL_CONTROL['FRIEND_NOT_IN_CALL']:
            raise RuntimeError('This client is currently not in a call with the friend. Before the call is answered, '
                               'only CANCEL is a valid control.')
        elif toxav_err_call_control == TOXAV_ERR_CALL_CONTROL['INVALID_TRANSITION']:
            raise RuntimeError('Happens if user tried to pause an already paused call or if trying to resume a call '
                               'that is not paused.')

    # -----------------------------------------------------------------------------------------------------------------
    # TODO Controlling bit rates
    # -----------------------------------------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------------------------------------
    # TODO A/V sending
    # -----------------------------------------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------------------------------------
    # TODO A/V receiving
    # -----------------------------------------------------------------------------------------------------------------
