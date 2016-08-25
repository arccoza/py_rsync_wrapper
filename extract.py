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
  return err, ver


re_doc_opts = re.compile(u'(?:(?:^\s-(?P<short>[^-\s,]),?)|(^\s*))(?:(?:\s--(?:(?:(?P<long>[^\s=]+)=?(?P<value>[^-\s]+)?(?:\s*(?P<desc>.*$)))))|(?:\s*same as(?P<same_as>\s--.*$)*))', re.MULTILINE)

def rsync_options():
  """Get rsync docs from the rsync command line."""
  rsync = pexpect.spawn(u'rsync --help')
  i = rsync.expect(pexpect.EOF)
  options = parse_rsync_options(rsync.before)
  pprint(options)
  

def parse_rsync_options(text):
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

  return short, long

rsync_options()