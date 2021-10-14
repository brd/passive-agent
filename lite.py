#!/usr/bin/env python

import argparse
import logging
import os
import requests
import signal
import sys

from passiveagent import check
from passiveagent import config
from passiveagent import schedule

global c
c = {}

def initialize_signal_handlers():
  signal.signal(signal.SIGHUP, handle_sighup)
  signal.signal(signal.SIGINT, handle_exit)
  signal.signal(signal.SIGTERM, handle_exit)

def handle_sighup(signal, frame):
  logging.warning('SIGHUP recieved, reloading config..')
  clear_sched(c)
  read_config(c)
  schedule.start_sched(c)

def handle_exit(signum, frame):
  logging.warning('%s recieved, exiting..', signal.strsignal(signum))
  remove_pid(c['pidfile'])
  sys.exit(0)

def remove_pid(pidfile):
  if os.path.isfile(pidfile):
    os.remove(pidfile)

def main():
  parser = argparse.ArgumentParser(description="Passive Agent")
  parser.add_argument('-c', '--configdir',
    default='/usr/local/etc/passiveagent',
    help='override the location of the configdir')
  parser.add_argument('-l', '--logfile', default='/var/log/lite.log',
    help='override the location of the logfile')
  parser.add_argument('-p', '--pidfile',
    default='/var/run/passiveagent.pid',
    help='override the location of the pidfile')
  args = parser.parse_args()
  c['config_dir'] = args.configdir

  # Setup logging
  logging.basicConfig(filename=args.logfile, level=logging.INFO,
    format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %I:%M:%S')
  logging.info('Starting up..')

  # Setup pidfile
  c['pidfile'] = args.pidfile
  try:
    with open(c['pidfile'], "w") as p:
      p.write(os.getpid())
  except:
    logging.error('Unable to create pidfile: %s', c['pidfile'])
    sys.exit(2)

  initialize_signal_handlers()

  config.read_config(c)
  schedule.start_sched(c)

if __name__ == '__main__':
  main()