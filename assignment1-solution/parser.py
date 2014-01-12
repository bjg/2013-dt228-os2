import os
import sys
import shlex
import glob
import logging
from command import Command
from collections import deque

class Parser():
  def __init__(self, spec, logger = None):
    self.logger = logger
    self.background = False
    self.cmds = self.parse(spec)

  # Splitting of input into constituent commands and arguments
  def parse(self, spec):
    lexer = shlex.shlex(spec)
    lexer.whitespace_split = True
    current = Command(self.logger)
    cmds = []
    redirecting_from = redirecting_to = False
    for arg in lexer:
      if redirecting_from:
        current.redirect_from(arg)
        continue
      elif redirecting_to:
        current.redirect_to(arg)
        continue
      if current.runnable():
        # Start of a new command
        cmds.append(current)
        current = Command(self.logger)
      if arg[0] == '"' or arg[0] == "'":
        # Argument is a string so strip the delimiters
        arg = arg[1:-1]
      elif arg == '&':
        self.background = True
        # The ampersand must be at the end of a command specification
        break
      elif arg == ';':
        current.end()
        continue
      elif arg == '|':
        current.end(piped = True)
        continue
      elif arg == '<':
        # Record that the next argument will be the input file
        redirecting_from = True
        continue
      elif arg == '>':
        # Record that the next argument will be the output file
        redirecting_to = True
        continue
      else:
        # Argument could be a file glob so attempt expansion in case
        expanded = glob.glob(arg)
        if len(expanded) > 0:
          current.extend(expanded)
          arg = None
      if arg:
        current.append(arg)
    if not current.runnable():
      current.end()
    if len(cmds) == 0 or cmds[-1] != current:
      cmds.append(current)
    return cmds

  def execute(self):
    pipe_fds = deque([None, None])
    for cmd in self.cmds:
      if cmd.piped:
        read, write = os.pipe()
        pipe_fds.pop()
        pipe_fds.extend([write, read, None])
      read = pipe_fds.popleft()
      write = pipe_fds.popleft()
      cmd.call(pipe_in = read, pipe_out = write, background = self.background)
      if read:
        os.close(read)
      if write:
        os.close(write)
