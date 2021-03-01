from chaslib.resptools import BasePersonality


class IDIntell1(BasePersonality):

    """
    CHAS Ideal intelligence 1.
    This personality is trianed on a dataset located here:
    https://www.kaggle.com/eibriel/rdany-conversations/data

    This is an attempt to create an ideal CHAS personality.
    """

    def __init__(self):

        # Instantiate the parent:

        super(BasePersonality).__init__("IDIntell1", "CHAS Ideal intelligence 1")

