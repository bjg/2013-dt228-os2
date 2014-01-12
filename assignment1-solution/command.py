import os
import sys

class Command():
  def __init__(self, logger = None):
    self.logger = logger
    self.piped = False
    self.infile = None
    self.outfile = None
    self.cmd = None
    self.args = []
    self.state = Command.INITIALISED

  def append(self, token):
    if self.state == Command.INITIALISED:
      self.cmd = token
      self.state = Command.BUILDING
    self.args.append(token)

  def extend(self, tokens):
    for token in tokens:
      self.append(token)

  def end(self, piped = False):
    if self.state == Command.RUNNABLE:
      return
    self.piped = piped
    self.state = Command.RUNNABLE

  def redirect_from(self, file):
    self.infile = file

  def redirect_to(self, file):
    self.outfile = file

  # Execute an external command (i.e. run a  program on disk)
  # If this succeeds this function never returns
  def __execute(self, cmd, pipe_in, pipe_out):
    if self.state != Command.RUNNABLE:
      return
    try:
      if self.infile:
        fd = os.open(self.infile, os.O_RDONLY)
        os.dup2(fd, 0)
      elif pipe_in:
        os.dup2(pipe_in, 0)
      if self.outfile:
        fd = os.open(self.outfile, os.O_CREAT | os.O_TRUNC | os.O_RDWR)
        os.dup2(fd, 1)
      elif pipe_out:
        os.dup2(pipe_out, 1)
      os.execv(cmd, self.args)
    except (IOError, OSError):
      pass

  def call(self, pipe_in, pipe_out, background):
    pid = os.fork()
    if pid == 0:
      if '/' in self.cmd:
        # Relative or absolute path specified
        self.__execute(self.cmd, pipe_in, pipe_out)
      else:
        for dir in os.getenv('PATH').split(':'):
          # Keep trying each directory in PATH until we find it
          self.__execute(dir + '/' + self.cmd, pipe_in, pipe_out)

      # If we get here then execution has failed
      sys.stderr.write('Unrecognised command: ' + self.cmd + '\n')
      os._exit(1)
    else:
      # If the command is background task, we don't do a wait
      if not background:
        try:
          os.wait()
        except OSError: pass

  def runnable(self):
    return self.state == Command.RUNNABLE

  def __repr__(self):
    return " ".join([self.cmd] + self.args)

Command.INITIALISED = 0
Command.BUILDING    = 1
Command.RUNNABLE    = 2
