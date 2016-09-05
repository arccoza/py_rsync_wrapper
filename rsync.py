import re
import pexpect
from helpers import RsyncError, Job
from pprint import pprint
import sys
import asyncio
from collections import OrderedDict


class Rsync(object):
  def __init__(self):
    self._rex = 'rsync'
    self._ver = None
    self._all_opts = None

  def set_executable(self, rex):
    self._rex = rex;

  def get_version(self):
    """Get the rsync version from the rsync command line."""
    rex = self._rex
    ver = None

    # TODO: Move the pexpect.spawn and exception handling into a mathod, perhaps __call__.
    try:
      rsync = spawn(rex + u' --version')
      i = rsync.expect(u'version\D*([\d\.]+)')
      ver = rsync.match.groups()[0]
    except (pexpect.EOF, pexpect.TIMEOUT, IndexError) as ex:
      raise RsyncError(u'version not found')
    except pexpect.ExceptionPexpect as ex:
      if u'command was not found or was not executable' in str(ex):
        raise RsyncError(u'command not found')
      else:
        raise RsyncError(u'unknown')
    self._ver = ver
    return ver

  # TODO: Add support for --info=FLAGS and --debug=FLAGS.
  def get_options(self):
    """Get rsync docs from the rsync command line."""
    rex = self._rex

    rsync = spawn(rex + u' --help')
    i = rsync.expect(pexpect.EOF)
    self._all_opts = self._parse_options(rsync.before.decode(sys.stdout.encoding))
    return self._all_opts

  def _parse_options(self, text):
    """Extract valid argument options from rsync docs."""
    short = {}
    long = {}
    for match in re_doc_opts.finditer(text):
      g = match.groupdict()

      # Split the same_as into individual long options, if it is found. (Couldn't be done in the regex).
      g[u'same_as'] = filter(None, g[u'same_as'].split(u' --')) if g[u'same_as'] else None

      if g[u'short']:
        short[g[u'short']] = {u'long': g[u'long'], u'value': g.get(u'value'), u'same_as':g[u'same_as'], u'desc': g[u'desc']}
      if g[u'long']:
        long[g[u'long']] = {u'short': g[u'short'], u'value': g.get(u'value'), u'desc': g[u'desc']}

    return {'short': short, 'long': long}

  def __call__(self, job):
    rex = self._rex
    cmd = None

    # try:
    #   cmd = job.render()
    # except AttributeError:
    #   if job is string_types:
    #     cmd = job
    #   else:
    #     for j in job:
    #       try:
    #         cmd = j.render()
    #       except AttributeError:
    #         cmd = j
    #       r = spawn(cmd)
    #     cmd = None
    # if cmd:
    #   r = spawn(cmd)

    try:
      for j in job:
        try:
          cmd = j.render()
        except AttributeError:
          if len(j) > 1:
            cmd = j
          else:
            raise TypeError()
        # r = spawn(cmd)
        pprint('---loop---')
        pprint(cmd)
    except TypeError:
      try:
        cmd = job.render()
      except AttributeError:
        cmd = job
      pprint('---single---')
      pprint(cmd)
      r = spawn(rex + ' ' + cmd)
      expected = Expected()
      try:
        for exp in expected(r):
          pprint(exp)
          if exp == 'password':
            r.sendline('carbonscape')
          elif exp == 'file':
            pprint(r.match.groups())
      except pexpect.EOF:
        pprint('---EOF---')
      # i = r.expect(['Password:', 'sending incremental file list', pexpect.EOF])
      # pprint(i)
      # if i == 0:
      #   pprint('---0')
      #   r.sendline('carbonscape')
      #   i = r.expect(['Password:', 'sending incremental file list', pexpect.EOF])
      # if i == 1:
      #   pprint('---1')
      #   # i = r.expect(['.*\r\n'])
      #   # pprint(r.match)
      #   # i = r.expect(['.*\r\n'])
      #   # pprint(r.match)
      #   # i = r.expect(['.*\r\n'])
      #   # pprint(r.match)
      #   while not r.eof():
      #     line = r.readline()
      #     pprint(line)
      # if i == 2:
      #   pprint('---2')
      #   pprint(r.before.decode(sys.stdout.encoding))

    
    # args = list(args)
    # args[0] = rex + ' ' + args[0]
    # pprint(args[0])
    # r = spawn(*args, **kwargs)
    # i = r.expect(['Password:', pexpect.EOF])
    # pprint(i)
    # pprint(r.match)
    # if(i == 0):
    #   b = r.sendline('carbonscape')
    #   pprint(b)
    #   i = r.expect(pexpect.EOF)
    #   pprint(r.before.decode(sys.stdout.encoding))
    # else:
    #   pprint(r.before.decode(sys.stdout.encoding))
    

  def list(self, job):
    pass

  def push(self, job):
    pass

  def pull(self, job):
    pass

  def sync(self, job):
    pass

re_doc_opts = re.compile(u'(?:(?:^\s-(?P<short>[^-\s,]),?)|(^\s*))(?:(?:\s--(?:(?:(?P<long>[^\s=]+)=?(?P<value>[^-\s]+)?(?:\s*(?P<desc>.*$)))))|(?:\s*same as(?P<same_as>\s--.*$)*))', re.MULTILINE)
spawn = pexpect.spawn
class Expected(OrderedDict):
  def __init__(self):
    super(Expected, self).__init__([
      ('[Pp]assword:?', 'password'),
      ('\s*\r\n', 'blank_line'),
      ('sending incremental file list.*\r\n', 'transfering'),
      ('sent\s*(?P<sent>[\d\.]+)\s*(?P<sent_units>\w*)\s*received\s*(?P<received>[\d\.]+)\s*(?P<received_units>\w*)\s*(?P<rate>[\d\.]+)\s*(?P<rate_units>[\w/]+)', 'transfered'),
      ('total\s*size\s*is\s*(?P<total_size>[\d\.,]+)\s*speedup\s*is\s*(?P<speedup>[\d\.,]+)\s*(?P<dry_run>.*DRY\s*RUN.*)?', 'summary'),
      ('/?(?P<file>[^/\0]+/?)\r\n', 'file'),
    ])

  def __call__(self, child):
    while not child.eof():
      index = child.expect(list(self.keys()))
      pprint('-----------------')
      # pprint(child.match.re.pattern.decode(sys.stdout.encoding))
      yield self[child.match.re.pattern.decode(sys.stdout.encoding)]



try:
  string_types = basestring
except NameError: 
  string_types = str

# def cb(*args, **kwargs):
#   pprint('---cb---')
#   pprint(args)
#   pprint(kwargs)

r = Rsync()
r('-avn --progress --filter="- */" /home/adrien/Videos/ root@al-mnemosyne.local::test/')

# # pprint(r.get_options())
# fut = r('--help')
# fut = next(fut)
# # fut = next(fut)
# fut.add_done_callback(cb)
# # pprint(fut)

# async def rex():  
#   return await fut

# loop = asyncio.get_event_loop()
# loop.run_until_complete(fut)
# loop.close()
# # for i in fut:
# #   pprint(i)

# # pprint(fut.result())

# # pprint(fut.done())

# # while not fut.done():
# #   pass

# # pprint(fut.done())
