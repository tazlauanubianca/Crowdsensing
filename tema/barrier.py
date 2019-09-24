"""
This module represents the implementation
of a reusable barrier.
"""
import threading

class ReusableBarrierSem(object):
    """
    Reusable Barrier implemented with semaphores.
    """

    def __init__(self, num_threads):
        """
        Constructor

        @type num_threads: Integer
        @param num_threads: number of threads that will be waited
        """
        self.num_threads = num_threads
        self.count_threads1 = self.num_threads
        self.count_threads2 = self.num_threads
        self.counter_lock = threading.Lock()
        self.threads_sem1 = threading.Semaphore(0)
        self.threads_sem2 = threading.Semaphore(0)

    def wait(self):
        """
        Function used for waiting all the threads
        """
        self.phase1()
        self.phase2()

    def phase1(self):
        """
        Function used for the first phase of the barrier
        """
        with self.counter_lock:
            self.count_threads1 -= 1
            if self.count_threads1 == 0:
                for _ in range(self.num_threads):
                    self.threads_sem1.release()
                self.count_threads1 = self.num_threads

        self.threads_sem1.acquire()

    def phase2(self):
        """
        Function used for the second phase of the barrier
        """
        with self.counter_lock:
            self.count_threads2 -= 1
            if self.count_threads2 == 0:
                for _ in range(self.num_threads):
                    self.threads_sem2.release()
                self.count_threads2 = self.num_threads

        self.threads_sem2.acquire()
