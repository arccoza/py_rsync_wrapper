from pprint import pprint


# def handler1(*args, **kwargs):
# 	pprint(u'handler1')
# 	pprint(args[0])

# def handler2(*args, **kwargs):
# 	pprint(u'handler2')
# 	pprint(args[0])

# def handler3(*args, **kwargs):
# 	pprint(u'handler3')
# 	pprint(args[0])

# def handler4(*args, **kwargs):
# 	pprint(u'handler4')
# 	pprint(args[0])


class Event(set):
	def __init__(self, h=()):
		try:
			super(Event,self).__init__(h)
		except TypeError:
			super(Event,self).__init__([h])

	def __call__(self, *args, **kwargs):
		for handler in self:
			handler(*args, **kwargs)
		if(len(self)):
			return True
		return False

	def __iadd__(self, other):
		try:
			self.add(other)
		except TypeError:
			self.update(other)
		return self

	def __isub__(self, other):
		try:
			self.remove(other)
		except TypeError:
			self.difference_update(other)
		return self

class Emitter(object):
	def __init__(self):
		self._events = {}

	def on(self, name, handler):
		try:
			self._events[name] += handler
		except KeyError:
			self._events[name] = Event(handler)

	def off(self, name=None, handler=None):
		try:
			self._events[name] -= handler
		except KeyError as ex:
			if handler == None and name == None:
				self._events.clear()
			elif handler == None:
				self._events[name].clear()
			else:
				raise ex

	def do(self, name, *args, **kargs):
		try:
			return self._events[name](*args, **kargs)
		except KeyError:
			return False

# e = Emitter()

# e.on(u'update', [handler1, handler2])
# e.on(u'update', [handler3, handler4])
# e.do(u'update', u'hello')
# e.off(u'update', [handler1, handler2])
# pprint(e.do(u'update', u'bye'))

