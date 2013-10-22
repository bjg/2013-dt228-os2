# Simple demonstration of how fork() works
import os

# At this point there is one process
pid = os.fork()

# Now there are two
#   1. The original (called the parent)
#   2. The new one (called the child)
# The fork() call returns in both processes. To determine which
# one you are in, you test the value of pid like this.

if pid == 0:
  # Child process
  print("This is the child!")
else:
  # Parent process
  print("This is the parent!")
