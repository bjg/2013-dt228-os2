import threading

# The ring buffer is a fixed sized list whose size should not exceed
# maxitems. It doesn't matter what you insert into the list, e.g.
# integers, strings, characters, whatever ...
maxitems = 10
# Need to size the buffer before it can be indexed
ringbuffer = [-1 for x in range(maxitems)]
readindex = 0
writeindex = 0
mutex = threading.Semaphore(value = 1)
spaceavail = threading.Semaphore(value = maxitems)
itemsavail = threading.Semaphore(value = 0)
 
# Class to represent a producer thread. Adds a new message to the
# global ring buffer and exits
class Producer(threading.Thread):
  def __init__(self, msg):
    threading.Thread.__init__(self)
    self.msg = msg

  def run(self):
    global ringbuffer, writeindex, mutex, spaceavail, itemsavail, maxitems
    # 1. Wait until a free buffer slot becomes available
    spaceavail.acquire()
    # 2. When one does, write the message into the buffer list, advancing
    #    the write index and accounting for write wrap around
    mutex.acquire()
    if writeindex == maxitems:
      writeindex = 0;
    ringbuffer[writeindex] = self.msg
    writeindex += 1
    mutex.release()
    # 3. Signal that there is one more message to read.
    itemsavail.release()
    return

class Consumer(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)

  def run(self):
    global ringbuffer, readindex, mutex, spaceavail, itemsavail, maxitems
    # 1. Wait until a message is available to process
    itemsavail.acquire()
    # 2. When a message becomes available, remove it from the message list,
    #    advancing the read index and handling read index wrapping
    mutex.acquire()
    if readindex == maxitems:
      readindex = 0
    msg =  ringbuffer[readindex]
    readindex += 1
    mutex.release()
    # 3. Print the message contents to the screen
    print(msg)
    # 4. Signal that a free message slot is available
    spaceavail.release()
    return

# Write some test code to create a number of producer and consumer threads
# Verify your bounded buffer implementation above for various numbers of each
#
# Note that you should follow the thread create, start and join pattern in shm2.py
# in order to make this work properly

T = 20

# Start some producers the same number of consumers
threads = []
for n in range(T):
  # Use the thread index as the unique message
  threads.append(Consumer())
  threads.append(Producer(msg = n))
# Set them running
for t in threads:
  t.start()
# And wait for everyone to finish
for t in threads:
  t.join()
