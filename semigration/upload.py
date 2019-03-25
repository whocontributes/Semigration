import re
import webbrowser
import urllib.parse

import clipboard
import pyreadline

from .section import URL_WIKI_BASE, URL_WIKI_PATH


URL_EDIT = f"https://{URL_WIKI_BASE}{URL_WIKI_PATH}index.php?title={{name}}&action=edit"

SHRINK_SPACE = re.compile(r'\s+')
BAD_PERCENT = re.compile(r'%[0-9a-fA-F]{2}')


def localize(msg, text, name="<>"):
	if msg.startswith("enter") and len(msg) > 5:
		num, total = msg[5:].split("/")
		return text.get(
			msg,
			text.get(
				f"enter{num}",
				text.get("enter#", "Enter name #{num}")
			)
		).format(num=num, total=total)

	return text.get(
		msg,
		{
			"badname": "Unable to use given page name, please enter a new one.\n  Invalid name: {name}",
			"suggest": 'Enter a new name or leave blank to use "{name}"',
			"enter": "Enter a name (or a number for multiple names)",
		}[msg]
	).format(name=name)


def upload(name, contents, text={}, bad=False):
	"""
	Step thru uploading a series of pages.

	name is either a string or a tuple of (namespace, name)
	"""
	namespace, cleaned = clean_name(name)
	if bad or cleaned is None:
		print(localize("badname", text, name))
		main_name, names = input_name(True, text)
	else:
		print(localize("suggest", text, name))
		main_name, names = input_name(False, text)

	if main_name:
		safe_main_name = names.pop(0)
	else:
		names.pop(0)  # pop off blank string
		main_name = add_ns(namespace, cleaned)
		safe_main_name = url_safe(namespace, cleaned)

	clipboard.copy(contents)
	webbrowser.open(URL_EDIT.format(name=safe_main_name))
	input("Press enter to continue...")

	for name in names:
		clipboard.copy(f"#REDIRECT [[{main_name}]]")
		webbrowser.open(URL_EDIT.format(name=name))
		input("Press enter to continue...")


def upload_all(pages):
	"""
	Step thru uploading a series of pages.

	pages is a dict of { name: contents, (namespace, name): contents }
	"""

	for name, contents in pages.items():
		upload(name, contents)


def input_name(blank_invalid, text):
	while True:
		msg = localize("enter", text)
		name = input(f"  {msg}: ")
		try:
			num = int(name)
		except ValueError:
			namespace, cleaned = clean_name(name)
			if cleaned is not None and (not blank_invalid or cleaned):
				return add_ns(namespace, cleaned), [url_safe(namespace, cleaned)]
			print("Name is invalid.")
		else:
			i = 1
			names = []
			while i <= num:
				msg = localize(f"enter{i}/{num}", text)
				name = input(f"  {msg}: ")
				namespace, cleaned = clean_name(name)
				if cleaned is not None and (not blank_invalid or cleaned):
					if i == 1:
						main_name = add_ns(namespace, cleaned)
					names.append(url_safe(namespace, cleaned))
					i += 1
				else:
					print("Name is invalid.")
			return main_name, names


def clean_name(name):
	if name is None:
		return None

	namespace = ""
	if isinstance(name, tuple):
		if len(name) > 2:
			raise ValueError("name")
		if len(name) == 2:
			namespace, name = name
		else:
			name = name[0]
	name = name.strip()

	if not name:
		return "", ""

	# https://www.mediawiki.org/wiki/Manual:Page_title#Invalid_page_titles
	for c in "#<>[]|{}_+":
		if c in name:
			return None

	if (
		name.startswith(":") or
		name in (".", "..") or
		name.startswith("./") or name.startswith("../") or
		"/./" in name or "/../" in name or
		name.endswith("/.") or name.endswith("/..") or
		len(name.encode("utf8")) > 255 or
		"~~~" in name or
		BAD_PERCENT.search(name)
	):
		return None

	name = name[0].upper() + name[1:]
	name = SHRINK_SPACE.sub(" ", name)

	return namespace, name


def add_ns(namespace, name):
	if namespace and name:
		return f"{namespace}:{name}"
	return name


def url_safe(namespace, name):
	return urllib.parse.quote(add_ns(namespace, name).replace(" ", "_"))
