import re
import json
import pexpect
from pprint import pprint

def rsync_version():
  ver = None
  err = None

  try:
    rsync = pexpect.spawn(u'rsync --version')
    i = rsync.expect(u'version\D*([\d\.]+)')
    ver = rsync.match.groups()[0]
  except (pexpect.EOF, pexpect.TIMEOUT, IndexError) as ex:
    err = u'version not found'
  except pexpect.ExceptionPexpect as ex:
    pprint(ex)
    if u'command was not found or was not executable' in str(ex):
      err = 'command not found'
    else:
      err = u'unknown'


rsync_version()