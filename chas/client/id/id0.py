# Dummy handler to get code working

from id.idhandle import IDHandle


class DummyHandel(IDHandle):

    def __init__(self):
        super(DummyHandel, self).__init__('Dummy Handler',
                                          'Dummy handler to get code working',
                                          0)

    def handel(self, dev, data):

        pass
