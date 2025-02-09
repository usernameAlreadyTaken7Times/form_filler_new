import queue
import threading

class MessageBroadcaster:
    def __init__(self):
        '''init'''
        self.queues = {}  # store all queues
        self.lock = threading.Lock()  # lock

    def register(self, logic_name) -> queue:
        '''register broadcaster queue for type'''
        with self.lock:
            if logic_name not in self.queues:
                self.queues[logic_name] = queue.Queue()
        return self.queues[logic_name]

    def broadcast(self, msg):
        '''broadcast message to all recivers'''
        with self.lock:
            for logic, q in self.queues.items():
                q: queue.Queue
                q.put(msg)  # all message format should be like {'source': 'xxx', 'command': 'xxx', 'content': 'xxx'}

# create a independent broadcaster for different services
broadcaster = MessageBroadcaster()