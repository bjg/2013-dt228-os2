import os
import mmap

def shmcreate():
  # Open the shared file for read/write, creating if necessary
  fd = os.open('shm1.dat', os.O_CREAT | os.O_TRUNC | os.O_RDWR)
  # Make it one page in length
  os.write(fd, b'\x00' * mmap.PAGESIZE)
  # Map it in
  shm = mmap.mmap(fd, mmap.PAGESIZE, mmap.MAP_SHARED, mmap.PROT_WRITE|mmap.PROT_READ)
  # We don't need the descriptor open now that it's mapped
  os.close(fd)
  return shm

msg = b"Hello, world!"
shm = shmcreate()
shm.write(msg)

pid = os.fork()
if pid == 0:
  # child
  shm.seek(0)
  print((shm.readline().decode('UTF-8')))
