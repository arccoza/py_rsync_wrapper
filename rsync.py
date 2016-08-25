import re
import pexpect
from helpers import RsyncError, Job
from pprint import pprint


class Rsync(object):
  def __init__(self):
    self._rex = 'rsync'
    self._ver = None
    self._all_opts = None

  def version(self):
    """Get the rsync version from the rsync command line."""
    rex = self._rex
    ver = None

    # TODO: Move the pexpect.spawn and exception handling into a mathod, perhaps __call__.
    try:
      rsync = pexpect.spawn(rex + u' --version')
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

  def options(self):
    """Get rsync docs from the rsync command line."""
    rex = self._rex

    rsync = pexpect.spawn(rex + u' --help')
    i = rsync.expect(pexpect.EOF)
    self._all_opts = self._parse_options(rsync.before)
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

  def _exec(self, job):
    p = pexpect.spawn(command)

  def list(self, job):
    pass

  def push(self, job):
    pass

  def pull(self, job):
    pass

  def sync(self, job):
    pass

re_doc_opts = re.compile(u'(?:(?:^\s-(?P<short>[^-\s,]),?)|(^\s*))(?:(?:\s--(?:(?:(?P<long>[^\s=]+)=?(?P<value>[^-\s]+)?(?:\s*(?P<desc>.*$)))))|(?:\s*same as(?P<same_as>\s--.*$)*))', re.MULTILINE)



r = Rsync()
pprint(r.options())