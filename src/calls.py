import pyaudio
import time
import threading
from util import log
from toxav_enums import *

CALL_TYPE = {
    'NONE': 0,
    'AUDIO': 1,
    'VIDEO': 2
}


class Call(object):
    # use instead of bit mask?
    def __init__(self, audio, video):
        self.audio, self.video = audio, video
        self.widget = None


class AV(object):

    def __init__(self, tox):
        self._toxav = tox.AV
        self._running = True

        self._calls = {}  # dict: key - friend number, value - call type

        self._audio = None
        self._audio_stream = None
        self._audio_thread = None
        self._audio_running = False

    def __contains__(self, friend_number):
        return friend_number in self._calls

    def __call__(self, friend_number):
        self._toxav.call(friend_number, 32, 5000)
        self._calls[friend_number] = CALL_TYPE['AUDIO']
        self.start_audio_thread()

    def finish_call(self, friend_number, by_friend=False):
        if not by_friend:
            self._toxav.call_control(friend_number, TOXAV_CALL_CONTROL['CANCEL'])
        del self._calls[friend_number]
        if not len(self._calls):
            self.stop_audio_thread()

    def stop(self):
        self._running = False
        self.stop_audio_thread()

    def start_audio_thread(self):
        if self._audio_thread is not None:
            return

        self._audio_running = True
        self._audio_rate = 8000
        self._audio_channels = 1
        self._audio_duration = 60
        self._audio_sample_count = self._audio_rate * self._audio_channels * self._audio_duration / 1000

        self._audio = pyaudio.PyAudio()

        self._audio_device_index = self._audio.get_default_output_device_info()['index']
        print 'Index', self._audio_device_index

        format_supported = self._audio.is_format_supported(self._audio_rate,
                                                           self._audio_device_index,
                                                           self._audio_channels,
                                                           pyaudio.paInt16)

        if not format_supported:
            self._audio_running = False
            del self._audio
            return

        self._audio_stream = self._audio.open(format=pyaudio.paInt16,
                                              rate=self._audio_rate,
                                              channels=self._audio_channels,
                                              input=True,
                                              input_device_index=self._audio_device_index,
                                              frames_per_buffer=self._audio_sample_count * 10)

        self._audio_thread = threading.Thread(target=self.audio_cb)
        self._audio_thread.start()

    def stop_audio_thread(self):

        if self._audio_thread is None:
            return

        self._audio_running = False

        self._audio_thread.join()

        self._audio_thread = None
        self._audio_stream = None
        self._audio = None

    def chunk(self, samples, samples_per_channel, channels_count, rate):
        # use other pyaudio inst?
        pya = self._audio
        stream = pya.open(format=pya.get_format_from_width(width=2), channels=channels_count, rate=rate, output=True)
        stream.write(samples)
        stream.stop_stream()
        stream.close()

    def audio_cb(self):

        while self._audio_running:
            try:
                pcm = self._audio_stream.read(self._audio_sample_count)
                if pcm:
                    for friend in self._calls:
                        if self._calls[friend] & 1:  # TODO: check if call started or play default sound
                            try:
                                self._toxav.audio_send_frame(friend, pcm, self._audio_sample_count,
                                                             self._audio_channels, self._audio_rate)
                            except Exception as ex:
                                log('Audio_cb ex in send frame: ' + str(ex))
            except Exception as ex:
                log('Audio_cb ex in read: ' + str(ex))

            time.sleep(0.01)

    def toxav_call_cb(self, friend_number, audio_enabled, video_enabled):

        if self._running:
            self._calls[friend_number] = int(video_enabled) * 2 + int(audio_enabled)
            self._toxav.answer(friend_number, 32, 5000)
            self.start_audio_thread()

    def toxav_call_state_cb(self, friend_number, state):
        if self._running:

            if state == TOXAV_FRIEND_CALL_STATE['FINISHED'] or state == TOXAV_FRIEND_CALL_STATE['ERROR']:
                del self._calls[friend_number]
                if not len(self._calls):
                    self.stop_audio_thread()

            if state & TOXAV_FRIEND_CALL_STATE['ACCEPTING_A']:
                self._calls[friend_number] |= 1
