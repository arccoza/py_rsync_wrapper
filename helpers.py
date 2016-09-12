import re
from pprint import pprint
from tools import PartialFormatter
from options import short_options, long_options


class Target(dict):
  def __init__(self, map_it_url=None):
    self._pat = re.compile(u'(?:(?:(?P<user>\S+)@)?(?P<server>[\w\-\.]+)(?P<method>:{1,2}))?(?P<module>[^:\\/\]]+)?(?P<path>/[^\0\r\n]*)')
    self._parts = ('user', 'server', 'method', 'module', 'path')
    self._methods = ('::', ':', '')
    self._method_types = ('rsync', 'rsh', 'local')

    if map_it_url:
      try:
        super(Target, self).__init__(map_it_url)
      except ValueError:
        self.parse(map_it_url)

  def parse(self, url):
    url = url[1:-1] if url[0] in '\'"' and url[-1] in '\'"' else url # Strip enclosing quotes if they exist.
    super(Target, self).update(self._pat.search(url).groupdict())

  def render(self):
    at = '@' if self['user'] else None
    return format('"{user}{at}{server}{method}{module}{path}"', at=at, **self)

  def update(self, *args, **kwargs):
    raise AttributeError("'" + self.__class__.__name__ +"' object has no attribute 'update'")

  def __setitem__(self, key, value):
    if key not in self._parts:
      raise KeyError("The key '" + key + "' is not allowed.")
    super(Target, self).__setitem__(key, value)

  def __missing__(self, key):
    if key in self._parts:
      return None
    else:
      raise KeyError(key)

  def __str__(self):
    return self.render()


class Options(dict):
  def __init__(self, map_it_opts=None):
    self._pat = re.compile('''(?:(?:^|\s)-(?P<sopt>[^-\s]+))|(?:(?:^|\s)--(?P<lopt>(?P<k>[^\-\s=]+)=?(?P<v>[^\-\s"']+|(?:["'].+?["']))?))''')

    if map_it_opts:
      try:
        super(Options, self).__init__(map_it_opts)
      except ValueError:
        self.parse(map_it_opts)

  def parse(self, opts_str):
    mats = self._pat.finditer(opts_str)
    for m in mats:
      m = m.groupdict()
      if m['k']:
        self[m['k']] = m['v']
      else:
        for o in m['sopt']:
          self[o] = None

  def render(self):
    opts = (format('--{opt}{eq}{val}', opt=k, val=v, eq='=' if v else None) for k, v in self.items())
    return ' '.join(opts)

  def update(self, *args, **kwargs):
    raise AttributeError("'" + self.__class__.__name__ +"' object has no attribute 'update'")

  def __setitem__(self, key, value):
    try:
      long = long_options[key]
      super(Options, self).__setitem__(key, value)
    except KeyError:
      try:
        short = short_options[key]
        super(Options, self).__setitem__(short['long'], short['value'])
      except KeyError:
        raise KeyError("The key '" + key + "' is not a valid option.")

  def __str__(self):
    return self.render()


class Job(object):
  def __init__(self, *args):
    self._pat = re.compile('''(?P<options>\s*(?:-{1,2}[^\s\-"']+(?:["'].+?["'])?\s+)*)(?:(?P<src>[^\s"']+|(?:["'].+["']))\s*(?P<dest>[^\s"']+|(?:["'].+["'])))''')
    self.src = Target()
    self.dest = Target()
    self.options = Options()

  def parse(self, cmd):
    mat = self._pat.match(cmd).groupdict()
    self.src.parse(mat['src'])
    self.dest.parse(mat['dest'])
    self.options.parse(mat['options'])
    # pprint(self.options)

  def render(self, options='', src='', dest=''):
    parts = [
      None if options is None else (options or self.options).render(),
      None if src is None else (src or self.src).render(),
      None if dest is None else (dest or self.dest).render(),
    ]
    parts = (v for v in parts if v)
    return ' '.join(parts)


class RsyncError(Exception):
  def __init__(self, message, errors=None):
    super(RsyncError, self).__init__(message)
    self.errors = errors


fmtr = PartialFormatter('', '')
format = fmtr.format


if __name__ == '__main__':
  # t = Target(u"root@al-mnemosyne.local::bob/videos/")
  # t.method = u':'
  # pprint(t.__dict__)
  # pprint(str(t))
  # a = Options()
  # a.grumble = True
  # a.parse(u'rsync -az -D --delete=1 --force vger.rutgers.edu::cvs/ /var/www/cvs/vger/')
  # pprint(a.__dict__)
  j = Job()
  j.parse('--progress -avi --filter="- */" --exclude=bob.avi --progress "/ho me/adrien/Videos/" root@al-mnemosyne.local::test/')
  pprint(j.render())
  # op = Options()
  # op.parse('--progress -avi --filter="- */" --exclude=bob.avi --progress')
  # pprint(op.render())
  # t = Target('al-mnemosyne.local::test/')
  # t['bob'] = 'sam'
  # t['user']
  # pprint(t)
