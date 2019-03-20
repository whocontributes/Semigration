from collections import OrderedDict

import mwclient
import mwparserfromhell

from .util import get_text

URL_WIKI_BASE = "wiki.mabinogiworld.com"
URL_WIKI_PATH = "/"


def parse(page):
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

	def get_templates(self, template_name):
		return [
			tp
			for tp in self.templates
			if tp.name == template_name
		]


class Template(OrderedDict):
	def __init__(self, template):
		OrderedDict.__init__(self, {})
		self._src = template
		self.name = get_text(template.name).strip()

		for param in template.params:
			key = get_text(param.name).strip()
			self[key] = param.value

	def text(self, key):
		return get_text(self[key]).strip()
