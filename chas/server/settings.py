# This file will contain the 'settings' class
# It will contain all configuration options

import speech_recognition as sr
from pocketsphinx import *
import os
from logging import DEBUG, WARN, WARNING, ERROR, CRITICAL, INFO


class Settings:

    def __init__(self):

        self.threads = []

        self.client_dir = os.path.dirname(os.path.abspath(__file__))
        self.extension_dir = os.path.join(self.client_dir, "extensions/")

        self.media_dir = os.path.join(self.client_dir, 'media/')

        self.id_dir = os.path.join(self.client_dir, 'id/')

        self.personality_dir = os.path.join(self.client_dir, 'personality/')

        self.log_file = 'log_chas.txt'  # Path to logging file
        self.log_file_level = DEBUG
        self.log_terminal_level = DEBUG

        self.host = '127.0.0.1'
        self.port = 65432

        self.socket_server = None

        self.wake = 'computer'

        # Pocket Sphinx Decoder options:

        config = Decoder.default_config()
        config.set_string('-logfn', 'log.txt')
        config.set_string('-hmm', os.path.join(get_model_path(), 'en-us'))
        config.set_string('-lm', os.path.join(get_model_path(), 'en-us.lm.bin'))
        config.set_string('-dict', os.path.join(get_model_path(), 'cmudict-en-us.dict'))
        config.set_string('-keyphrase', 'computer')
        config.set_float('-kws_threshold', 1e-40)

        self.decoder = pocketsphinx.Decoder(config)
