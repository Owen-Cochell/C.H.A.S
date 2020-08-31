
# The template for creating ID handlers


class IDHandle(object):

    def __init__(self, name, desc, id_num):

        self.name = name  # Name of the handler
        self.description = desc  # Description of the handler
        self.id_num = id_num  # ID number of the handler

    def handel(self, dev, data):

        pass

    def set_chas(self, chas):

        """
        Function for setting the CHAS Masterclass
        :param chas: Instance of the CHAS Masterclass
        :return:
        """

        self.chas = chas

    def get_id(self):

        return self.id_num
