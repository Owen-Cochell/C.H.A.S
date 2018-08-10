#Test file for connections
class serverinfo:

    def __init__(self, ip, hostname, typec):
        self.ip = ip
        self.hostname = hostname
        self.typec = typec
        return

server = serverinfo('10.0.0.3', 'Melanie', 'SSH')
print("Testing connection to: {} IP: {} Type: {}".format(server.hostname, server.ip, server.typec))
