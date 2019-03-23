from collections import OrderedDict

from .util import get_text
from .style import StyleDict

class Html:
	def __init__(self, code):
		tag = get_text(code.tag).strip().lower()
		attrs = self.attrs = OrderedDict()
		style = self.style = StyleDict()
		self.contents = code.contents
		self.text = get_text(code.contents)

		for attr in code.attributes:
			name = get_text(attr.name).strip().lower()
			value = get_text(attr.value)

			if name == "style":
				for kv in value.strip().strip(";").split(";"):
					sk, sv = kv.split(":", 1)
					style[sk.strip()] = sv.strip()
			else:
				attrs[name] = value

		if tag == "font":
			self.tag = "span"

			if "color" in attrs:
				style["color"] = attrs["color"]
				del attrs["color"]
		else:
			self.tag = tag
