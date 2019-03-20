import re
from collections import OrderedDict

from . import color

class StyleDict(OrderedDict):
	_replacer = re.compile(r'-(.)')

	def _sub(mo):
		return mo.group(1).upper()

	def _norm_one(fun):
		def handler(self, key, *args):
			return fun(self, self._replacer.sub(self._sub, key), *args)
		return handler

	def _norm_dict(fun):
		def handler(self, d={}):
			return fun(self, OrderedDict([
				(self._replacer.sub(self._sub, k), v)
				for k, v in (d.items() if hasattr(d, "items") else d)
			]))
		return handler

	__init__ = _norm_dict(OrderedDict.__init__)

	@_norm_one
	def __getitem__(self, key):
		value = OrderedDict.__getitem__(self, key)
		try:
			fun = object.__getattribute__(self, f"get_{key}")
		except AttributeError:
			return value
		else:
			return fun(value)

	@_norm_one
	def __setitem__(self, key, value):
		try:
			fun = object.__getattribute__(self, f"set_{key}")
		except AttributeError:
			print(f"set_{key} not found")
			OrderedDict.__setitem__(self, key, value)
		else:
			OrderedDict.__setitem__(self, key, fun(value))

	__delitem__ = _norm_one(OrderedDict.__delitem__)
	__getattr__ = __getitem__
	__setattr__ = __setitem__
	__delattr__ = __delitem__

	def _norm_color(self, value):
		if isinstance(value, str):
			value = value.lower()
			if value.startswith("#"):
				hx = value[1:]
				third = len(hx) / 3
				twothird = third * 2

				return (
					int(hx[:third], 16),
					int(hx[third:twothird], 16),
					int(hx[twothird:], 16),
				)
			elif value.startswith("rgb("):
				values = value[4:-1].split(",")

				return tuple(
					int(x[:-1]) * 255 / 100 if x.endswith("%") else int(x.strip())
					for x in values
				)
			try:
				return getattr(color, value)
			except AttributeError:
				raise ValueError(f"unknown name (or form) {value}")
		elif isinstance(value, tuple):
			if len(value) != 3:
				raise ValueError("color tuples must be RGB")
			return value
		raise ValueError("expected valid color format")

	set_color = _norm_color
