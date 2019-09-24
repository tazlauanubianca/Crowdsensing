"""
This module represents a device.

Computer Systems Architecture Course
Assignment 1
March 2019
"""
from threading import Event, Thread, Lock
import barrier
import thread_pool

class Device(object):
    """
    Class that represents a device.
    """

    def __init__(self, device_id, sensor_data, supervisor):
        """
        Constructor.

        @type device_id: Integer
        @param device_id: the unique id of this node; between 0 and N-1

        @type sensor_data: List of (Integer, Float)
        @param sensor_data: a list containing (location, data) as measured by this device

        @type supervisor: Supervisor
        @param supervisor: the testing infrastructure's control and validation component
        """
        self.device_id = device_id
        self.sensor_data = sensor_data
        self.supervisor = supervisor
        self.script_received = Event()
        self.scripts = []
        self.timepoint_done = Event()
        self.barrier = None
        self.locations = dict()
        self.lock = Lock()

        self.thread = DeviceThread(self)
        self.thread.start()

    def __str__(self):
        """
        Pretty prints this device.

        @rtype: String
        @return: a string containing the id of this device
        """
        return "Device %d" % self.device_id

    def setup_devices(self, devices):
        """
        Setup the devices before simulation begins.

        @type devices: List of Device
        @param devices: list containing all devices
        """
        if self.device_id == 0:
            self.barrier = barrier.ReusableBarrierSem(len(devices))

            for device in devices:
                device.set_concuring_devices(self.barrier, \
                                             self.lock, \
                                             self.locations)

    def set_concuring_devices(self, common_barrier, \
                                    common_lock, \
                                    locations):
        """
        Function that sets the same barrier, lock and location dictionary to all devices.

        @type common_barrier: Barrier
        @param common_barrier: barrier used to synchronize devices

        @type common_lock: Lock
        @param common_lock: lock used to synchronize access to variables

        @type locations: Dictionary
        @param locations: dictionary with locations and locks
        """
        self.barrier = common_barrier
        self.lock = common_lock
        self.locations = locations

    def assign_script(self, script, location):
        """
        Provide a script for the device to execute.

        @type script: Script
        @param script: the script to execute from now on at each timepoint; None if the
            current timepoint has ended

        @type location: Integer
        @param location: the location for which the script is interested in
        """
        if script is not None:
            self.script_received.set()
            self.scripts.append((script, location))

            with self.lock:
                if location is not None:
                    if location not in self.locations:
                        self.locations[location] = Lock()

        else:
            self.timepoint_done.set()

    def get_data(self, location):
        """
        Returns the pollution value this device has for the given location.

        @type location: Integer
        @param location: a location for which obtain the data

        @rtype: Float
        @return: the pollution value
        """
        if location in self.sensor_data:
            return self.sensor_data[location]

        return None

    def set_data(self, location, data):
        """
        Sets the pollution value stored by this device for the given location.

        @type location: Integer
        @param location: a location for which to set the data

        @type data: Float
        @param data: the pollution value
        """
        if location in self.sensor_data:
            self.sensor_data[location] = data

    def shutdown(self):
        """
        Instructs the device to shutdown (terminate all threads). This method
        is invoked by the tester. This method must block until all the threads
        started by this device terminate.
        """
        self.thread.join()

class DeviceThread(Thread):
    """
    Class that implements the device's worker thread.
    """

    def __init__(self, device):
        """
        Constructor.

        @type device: Device
        @param device: the device which owns this thread
        """
        Thread.__init__(self, name="Device Thread %d" % device.device_id)
        self.device = device
        self.number_subthreads = 8
        self.subthreads = thread_pool.ThreadPool(self.number_subthreads)

    def run(self):
        """
        Function executed by the thread.
        """
        while True:
            neighbours = self.device.supervisor.get_neighbours()
            if neighbours is None:
                for _ in range(self.number_subthreads):
                    self.subthreads.add_task(None)
                break

            self.device.timepoint_done.wait()
            for (script, location) in self.device.scripts:
                self.subthreads.add_task((script, location, self, neighbours))

            self.device.timepoint_done.clear()
            self.device.barrier.wait()

        self.subthreads.finish()
