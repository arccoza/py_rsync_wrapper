import re
from pprint import pprint
from tools import PartialFormatter
from options import short_options, long_options


class Target(dict):
  def __init__(self, map_it_url=None):
    self.pat = re.compile(u'(?:(?:(?P<user>\S+)@)?(?P<server>[\w\-\.]+)(?P<method>:{1,2}))?(?P<module>[^:\\/\]]+)?(?P<path>/[^\0\r\n]*)')
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
    super(Target, self).update(self.pat.search(url).groupdict())
    self['user'] = self.get('user') # Force the 'at' key to update.

  def render(self):
    return format('{user}{at}{server}{method}{module}{path}', **self)

  def update(self, *args, **kwargs):
    raise AttributeError("'" + self.__class__.__name__ +"' object has no attribute 'update'")

  def __setitem__(self, key, value):
    if key not in self._parts:
      raise KeyError("The key '" + key + "' is not allowed.")
    super(Target, self).__setitem__(key, value)
    if key == 'user':
      super(Target, self).__setitem__('at', '@' if value else None)

  def __missing__(self, key):
    if key in self._parts:
      return None
    else:
      raise KeyError(key)

  def __str__(self):
    return self.render()


class OldTarget(object):
  def __init__(self, url=None):
    self.re_url = re.compile(u'(?:(?:(?P<user>\S+)@)?(?P<server>[\w\-\.]+)(?P<method>:{1,2}))?(?P<module>[^:\\/\]]+)?(?P<path>/[^\0\r\n]*)')
    self.parts = {} #user, server, method, module, path
    self._methods = ('::', ':', '')
    self._method_types = ('rsync', 'rsh', 'local')
    
    if url:
      self.parse(url)

    # test_str = u"root@al-mnemosyne.local::bob/videos/"
    # pprint(re.search(self.re_url, test_str).groupdict())
    # pass

  def parse(self, url):
    self.parts = re.search(self.re_url, url).groupdict() if url else {}
    # Trigger self.method_type set.
    self.method = self.method
    self.parts['at'] = '@' if self.parts.get('user') else ''

  def render(self):
    fmtr = PartialFormatter('', '')
    url = fmtr.format('{user}{at}{server}{method}{module}{path}', **self.parts)
    return url

  def __setattr__(self, key, value):
    try:
      if key != 'parts' and key in self.parts:
        # Make sure to update method_type when method is updated.
        if key == 'method':
          self.parts[key] = value if value in self._methods else self.parts.get(key, None)
          self.parts[u'method_type'] = u'rsync' if self.parts[key] == '::' else u'rsh' if self.parts[key] == ':' else u'local'
        # Make sure to update method when method_type is updated.
        elif key == 'method_type':
          self.parts[key] = value if value in self._method_types else self.parts.get(key, 'local')
          self.parts[u'method'] = u'::' if self.parts[key] == 'rsync' else u':' if self.parts[key] == 'rsh' else u''
        # Update self.parts['at'] if self.user changes.
        elif key == 'user':
          self.parts['at'] = '@' if value else ''
        # Ignore attempts to update self.at.
        elif key == 'at':
          pass
        else:
          self.parts[key] = value
      else:
        raise AttributeError(key)
    except Exception as ex:
      # pprint(ex)
      self.__dict__[key] = value

  def __getattr__(self, key):
    if key != 'parts':
      return self.parts[key]
    else:
      raise AttributeError(key)

  def __str__(self):
    return self.render()

class Options(dict):
  def __init__(self, map_it_opts=None):
    self.pat = re.compile('''(?:(?:^|\s)-(?P<sopt>[^-\s]+))|(?:(?:^|\s)--(?P<lopt>(?P<k>[^\-\s=]+)=?(?P<v>[^\-\s"']+|(?:["'].+?["']))?))''')

    if map_it_opts:
      try:
        super(Options, self).__init__(map_it_opts)
      except ValueError:
        self.parse(map_it_opts)

  def parse(self, opts_str):
    mats = self.pat.finditer(opts_str)
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


class OldOptions(object):
  def __init__(self, *args):
    self.re_opts = re.compile(u'(?:(?:^|\s)-(?P<sopt>[^-\s]+))|(?:(?:^|\s)--(?P<lopt>(?P<k>[^-\s=]+)=?(?P<v>[^-\s])?))')
    self._short = {}
    self._long = {}
    self._opts = {}

  def parse(self, opts_str):
    mchs = self.re_opts.finditer(opts_str) if opts_str else {}
    opts = {}
    # opts = {o:m['v'] for m in [m.groupdict() for m in mchs] for o in (lambda m: m['sopt'] if m['sopt'] else [m['k']])(m)}
    for m in mchs:
      m = m.groupdict()
      if m['k']:
        opts[m['k']] = m['v']
      else:
        for o in m['sopt']:
          opts[short_options[o]['long']] = short_options[o]['value']
    pprint(opts)
    # for o in opts:
    #   pprint(o.groupdict())
    # pprint(opts)

  def render(self):
    return ''

  # TODO: Add option key handling, with special cases for --info=FLAGS and --debug=FLAGS.
  # def __setattr__(self, key, value):
  #   if key in (u'_short', u'_long'):
  #     self.__dict__[key] = value
  #     return

  #   try:
  #     long_key = short_options[key] if len(key) == 1 else None
  #   except KeyError as ex:
  #     pass

  #   try:
  #     short_key = long_options[key] if len(key) > 1 else None
  #   except KeyError as ex:
  #     pass


class Job(object):
  def __init__(self, *args):
    self.pat = re.compile('''(?P<options>\s*(?:-{1,2}[^\s\-"']+(?:["'].+?["'])?\s+)*)(?:(?P<src>[^\s"']+|(?:["'].+["']))\s*(?P<dest>[^\s"']+|(?:["'].+["'])))''')
    self.src = Target()
    self.dest = Target()
    self.options = Options()

  def parse(self, cmd):
    mat = self.pat.match(cmd).groupdict()
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
