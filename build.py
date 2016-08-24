import re
import json
from pprint import pprint


p = re.compile(u'(?:(?:^\s-(?P<short>[^-\s,]),?)|(^\s*))(?:(?:\s--(?:(?:(?P<long>[^\s=]+)=?(?P<value>[^-\s]+)?(?:\s*(?P<desc>.*$)))))|(?:\s*same as(?P<same_as>\s--.*$)*))', re.MULTILINE)
test_str = u" -v, --verbose               increase verbosity\n     --info=FLAGS            fine-grained informational verbosity"

def extract_rsync_options(text):
  """Extract valid argument options from rsync docs."""
  short = {}
  long = {}
  for match in re.finditer(p, text):
    g = match.groupdict()

    if g[u'short']:
      short[g[u'short']] = {u'long': g[u'long'], u'value': g.get(u'value'), u'desc': g[u'desc']}
    if g[u'long']:
      long[g[u'long']] = {u'short': g[u'short'], u'value': g.get(u'value'), u'desc': g[u'desc']}

  return short, long

def dump_rsync_options(text, fname):
  """Dump the extracted rsync options to a json file."""
  short, long = extract_rsync_options(text)
  with open(fname, mode='w') as f:
    json.dump({u'short': short, u'long': long}, f)

def rsync_options_task():
  with open('src/rsync_options.txt') as f:
    dump_rsync_options(f.read(), 'options.json')

if __name__ == '__main__':
  # short, long = extract_rsync_options(test_str)
  # pprint(short)
  # pprint('-----')
  # pprint(long)
  rsync_options_task()