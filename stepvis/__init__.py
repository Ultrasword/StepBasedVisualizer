import time
import threading
from queue import deque

# --------------------------- #
# task scheduler class

class StepVisScheduler(threading.Thread):
    FREQUENCY = "freq"
    DEFAULT_FREQ = 10

    PAUSE_TIME = "ptime"

    ATTEMPT_JOIN_TIME = 2

    def __init__(self, arguments = {}):
        self._params = {}
        super().__init__(target=self._target, daemon=True)
        # set variables
        for i, j in arguments.items():
            self[i] = j
        # check for certain variables
        if self.FREQUENCY not in self._params:
            self[self.FREQUENCY] = self.DEFAULT_FREQ
        self[self.PAUSE_TIME] = 1/self[self.FREQUENCY]
        
        # fini
        self.running = True
        self._task_queue = deque()
        
    def _target(self):
        while self.running:
            time.sleep(self[self.PAUSE_TIME])
            # print(self._task_queue)
            # run a task
            self.run_task()
        
    def run_task(self):
        """Run a task"""
        if not self._task_queue: return
        func, args = self._task_queue.popleft()
        func(*args)
        
    def kill(self):
        """Kill the task scheduler"""
        self.running = False
        super().kill()

    def push_task(self, target, args=()):
        """Push a task to the queue"""
        self._task_queue.append((target, args))

    def attempt_join(self):
        """Attempt to join a thread"""
        time.sleep(self.ATTEMPT_JOIN_TIME)
        if self.is_alive():
            self.kill()

    def __getitem__(self, item):
        """Get an item -- dictionary"""
        return self._params.get(item)

    def __setitem__(self, key, value):
        """Set an item -- dictionary"""
        self._params[key] = value

    def __contains__(self, item):
        """Check if self contains an item"""
        return item in self._params
    
    def __len__(self):
        """Get the length of the task queue"""
        return len(self._task_queue)



