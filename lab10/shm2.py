import threading

# Protect the critical region
mutex = threading.BoundedSemaphore(value = 1)
# An integer counter shared between threads
counter = 0
# Whether to run synchronised or not
Synchronised = True
# How many threads
T = 10
# Count upper bound
Max = 100000

class MyCounter(threading.Thread):
  def __init__(self, N):
    threading.Thread.__init__(self)
    self.N = N

  def run(self):
    global mutex
    global counter
    global Synchronised
    for i in range(self.N):
      if Synchronised:
        mutex.acquire()
        counter += 1
        mutex.release()
      else:
        counter += 1

threads = []
for n in range(T):
  t = MyCounter(N = Max)
  t.start()
  threads.append(t)

# Wait for everyone to finish
for t in threads:
  t.join()

print(counter)
assert counter == T * Max
