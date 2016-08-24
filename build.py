import re
import json
from pprint import pprint


re_opts = re.compile(u'(?:(?:^\s-(?P<short>[^-\s,]),?)|(^\s*))(?:(?:\s--(?:(?:(?P<long>[^\s=]+)=?(?P<value>[^-\s]+)?(?:\s*(?P<desc>.*$)))))|(?:\s*same as(?P<same_as>\s--.*$)*))', re.MULTILINE)


def parse_rsync_options(text):
  """Extract valid argument options from rsync docs."""
  short = {}
  long = {}
  for match in re_opts.finditer(text):
    g = match.groupdict()

    # Split the same_as into individual long options, if it is found. (Couldn't be done in the regex).
    g[u'same_as'] = filter(None, g[u'same_as'].split(u' --')) if g[u'same_as'] else None

    if g[u'short']:
      short[g[u'short']] = {u'long': g[u'long'], u'value': g.get(u'value'), u'same_as':g[u'same_as'], u'desc': g[u'desc']}
    if g[u'long']:
      long[g[u'long']] = {u'short': g[u'short'], u'value': g.get(u'value'), u'desc': g[u'desc']}

  return short, long

def dump_rsync_options(text, fname):
  """Dump the extracted rsync options to a json file."""
  short, long = parse_rsync_options(text)
  with open(fname, mode='w') as f:
    json.dump({u'short': short, u'long': long}, f, sort_keys=True, indent=2)

def extract_rsync_options():
  with open('src/rsync_options.txt') as f:
    dump_rsync_options(f.read(), 'options.json')

if __name__ == '__main__':
  extract_rsync_options()