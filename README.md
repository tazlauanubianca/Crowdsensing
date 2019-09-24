# Crowdsensing implementation details

Implementation of a system of crowdsensing using 
multiple moving devices. The devices are responsible for collecting
data and applying a script on them to interpret the data.

The main implementation is in device module which contains
the device class responsible for starting the main device thread 
that will de the work and will keep track of all the data collected
so far for different areas.

The ThreadDevice class will work through multiple subthreads. 
In our case, a number of 8 threads will be started in the begining.
The subthreads will be managed through the ThreadPool class. The main 
thread will just keep track of the timepoints. At the begining of each 
timepoint, the thread will wait until all the scripts have been received 
and will check if it has neighbours. If it doesn't have any neighbours 
it knows it has to stop and will signal that to the subthreads too, 
so they will know they have to stop. If the main thread has neighbours 
and all the scripts were received, individual tasks will be
created for each script and will be added in the task queue for the
subthreads. When all the work was completed by the subthreads, the
main thread will wait at a barrier for all the devices to finish 
their respective timepoint until it will continue to the next
iteration.

The ThreadPool class is responsible for actually managing
the work between the multiple threads. It will use a queue where
all the tasks will be placed and each thread will take a task from
it to execute it. To coordinate which thread collects data for which
location at a given time it uses locks for each location.

A dictionary was created in the device class that keeps an 
entry for every known location by the device and a lock for it. The 
dictionary is the same one for all the devices, only the first device
sharing it with the rest.

When all the timepoints were completed, the threads will stop
when they will get a None in the queue, that will break the while loop
which will cause to stop them working.

