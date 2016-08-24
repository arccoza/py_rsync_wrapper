import re
from pprint import pprint
from tools import PartialFormatter
from options import short_options, long_options


class Target(object):
  def __init__(self, url=None):
    self.re_url = re.compile(u'(?:(?P<user>\w+)@)?(?P<server>[a-zA-Z0-9\-\.]+)?(?P<method>::|:)?(?P<module>[a-zA-Z0-9\-\.]+)?(?P<path>/{1}[a-zA-Z0-9\-\./]+)')
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


class Options(object):
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
    pass

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
    self.local = Target()
    self.remote = Target()
    self.options = Options()

  def list(self, target='remote'):
    pass

  def push(self):
    pass

  def pull(self):
    pass

  def sync(self):
    pass



if __name__ == '__main__':
  # t = Target(u"root@al-mnemosyne.local::bob/videos/")
  # t.method = u':'
  # pprint(t.__dict__)
  # pprint(str(t))
  a = Options()
  a.grumble = True
  a.parse(u'rsync -az -D --delete=1 --force vger.rutgers.edu::cvs/ /var/www/cvs/vger/')
  # pprint(a.__dict__)
