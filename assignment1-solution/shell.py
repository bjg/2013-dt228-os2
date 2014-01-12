# Very basic Posix shell
import sys
import readline
from parser import Parser
import logging

prompt = "sh>> "

logger = logging.getLogger('shell')
hdlr = logging.FileHandler('./shell.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)

def copyright():
  sys.stderr.write("""
Copyright (C) 2012-13 Brian Gillespie
This program comes with ABSOLUTELY NO WARRANTY; This is free
software, and you are welcome to redistribute it under certain
conditions; Type "copyright" or "license" for more information.
""" + "\n")

copyright()
# Read, print, eval, loop (REPL)
while True:
  try:
    cmd = input(prompt).strip()
    if cmd == "":
      # Empty command so just prompt again
      pass
    elif cmd == "exit":
      # Exit the shell
      break
    elif cmd == "copyright":
      copyright()
    else:
      Parser(cmd, logger).execute()
  except EOFError:
    # User has pressed Ctrl-D so exit the shell
    break
