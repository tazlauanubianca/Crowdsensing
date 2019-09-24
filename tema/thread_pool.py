"""
This module represents the implementation of a thread pool.
"""
from threading import Thread
import Queue

class ThreadPool(object):
    """
    Class that represents a thread pool for the main thread device.
    """

    def __init__(self, number_threads):
        """
        Constructor.

        @type number_threads: Integer
        @param number_threads: number of threads that will be used.
        """
        self.number_threads = number_threads
        self.queue = Queue.Queue()
        self.threads = []

        for _ in range(number_threads):
            new_thread = Thread(target=self.thread_function)
            self.threads.append(new_thread)
            new_thread.start()

    @staticmethod
    def execute_task((script, location, master_thread, \
                                                neighbours)):
        """
        Executes the script in the task with the given location.

        @type script: Script
        @param script: thre script to be executed on a given set of data.

        @type location: Integer
        @param location: the location for which the data is needed

        @type master_thread: DeviceThread
        @param master_thread: the thread to which the current thread blongs to.

        @type neighbours: List
        @param neighbours: list of neigbouring devices.
        """
        script_data = []
        master_thread.device.locations[location].acquire()

        for device in neighbours:
            data = device.get_data(location)
            if data is not None:
                script_data.append(data)

        data = master_thread.device.get_data(location)
        if data is not None:
            script_data.append(data)

        if script_data != []:
            result = script.run(script_data)

            for device in neighbours:
                device.set_data(location, result)

            master_thread.device.set_data(location, result)

        master_thread.device.locations[location].release()

    def thread_function(self):
        """
        Function executed by every thread in the thread pool.
        """
        while True:
            task = self.queue.get()

            if task is None:
                self.queue.task_done()
                break
            else:
                self.execute_task(task)
                self.queue.task_done()

    def add_task(self, task):
        """
        Function that adds a new task in the queue.

        @type task: Touple
        @param task: a touple containing the script, location,
                     master thread and neighbours needed for
                     the script to be executed.
        """
        self.queue.put(task)

    def finish(self):
        """
        Function that finishes the execution of all threads in
        the thread pool.
        """
        self.queue.join()

        for thread in self.threads:
            thread.join()
