from collections import OrderedDict

import mwclient
import mwparserfromhell

from .util import get_text

URL_WIKI_BASE = "wiki.mabinogiworld.com"
URL_WIKI_PATH = "/"


def parse(page=None, *, text=None):
	if text is None:
		site = mwclient.Site(URL_WIKI_BASE, URL_WIKI_PATH)
		text = site.pages[page].text()

	parsed = mwparserfromhell.parse(text)

	root = Section(page)

	last_headers = [root]
	last_header_level = 1

	for node in parsed.nodes:
		if isinstance(node, mwparserfromhell.nodes.heading.Heading):
			title = get_text(node.title).strip()
			if node.level <= last_header_level:
				for i in range(node.level, last_header_level+1):
					last_headers.pop()
			last_headers.append(last_headers[-1].add_section(title))
			last_header_level = node.level
		elif isinstance(node, mwparserfromhell.nodes.template.Template):
			last_headers[-1].add_template(node)

	return root


def download(pages):
	root = Section("Batch")

	for page in pages:
		root.headers[page] = parse(page)

	return root


class Section:
	def __init__(self, title):
		self.title = title
		self.headers = OrderedDict()
		self.templates = []

	def add_section(self, title):
		section = Section(title)
		self.headers[title] = section
		return section

	def add_template(self, template):
		self.templates.append(Template(template))

	def __getitem__(self, key):
		return self.headers[key]

	def get_templates(
		self, *,
		name=None,
		params={},
		default=None,
	):
		return [
			tp
			for tp in self.templates
			if (
				(name is None or tp.name == name) and
				(params is None or all(
					p in tp and (lambda x: x in v if isinstance(v, (list, tuple)) else x == v)(
						get_text(tp[p], default).strip()
					)
					for p, v in params.items()
				))
			)
		]

	def text(self, level=1):
		eq = "=" * level
		return "\n".join((
			f"{eq} {self.title} {eq}",
			*(str(tp._src) for tp in self.templates),
			*(head.text(level + 1) for head in self.headers.values()),
		))


class Template(OrderedDict):
	def __init__(self, template):
		OrderedDict.__init__(self, {})
		self._src = template
		self.name = get_text(template.name, str).strip()

		for param in template.params:
			key = get_text(param.name).strip()
			self[key] = param.value

	def text(self, key):
		return get_text(self[key]).strip()

	def __repr__(self):
		return f"{self.__class__.__name__}({repr(self.name)}, [{', '.join(repr(s) for s in self.items())}])"
