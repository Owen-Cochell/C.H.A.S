from chaslib.resptools import Personality
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, UbuntuCorpusTrainer


class Chatter(Personality):

    """
    CHAS Chatter personality
    """

    def __init__(self):

        super(Chatter, self).__init__('Chatter', 'CHAS Chatterbot Implementation')
        self.bot = None  # Bot instance, loaded at start time to prevent excessive load times

    def start(self):

        """
        Start method, loading chatbot and database
        """

        self.bot = ChatBot('CHAS',
                           storage_adapter='chatterbot.storage.SQLStorageAdapter',
                           database_uri='sqlite:///db.sqlite3')

    def handel(self, mesg, talk, win):

        """
        Handles input from uses and passes information through the chatbot
        :param mesg: Input from user
        :param talk: Value weather we are talking
        :param win: Output object
        :return:
        """

        response = self.bot.get_response(mesg)

        win.add(response.text, output="CHATTER")
