import zmq
from pyre import Pyre


class Network():
    def __init__(self):
        self.node = Pyre("GAME_NODE")
        self.node.set_header("HELLO", "ABC")
        self.node.start()
        self.node.join("world:position")

        self.poller = zmq.Poller()
        self.poller.register(self.node.socket(), zmq.POLLIN)

    def poll(self):
        return dict(self.poller.poll(0))

    def peers(self):
        return self.node.peers()

    def stop(self):
        self.node.stop()

    def get_events(self):
        changes = self.poll()
        if self.node.socket() in changes and changes[self.node.socket()] == zmq.POLLIN:
            events = self.node.recent_events()
            return events


