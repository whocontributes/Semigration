import string
import unicodedata

import mwparserfromhell

def get_text(code):
	if code is None: return ""

	if isinstance(code, mwparserfromhell.wikicode.Wikicode):
		return "".join(get_text(node) for node in code.nodes)
	if isinstance(code, mwparserfromhell.nodes.text.Text):
		return code.value
	if isinstance(code, mwparserfromhell.nodes.wikilink.Wikilink):
		return get_text(code.text or code.title)
	if isinstance(code, mwparserfromhell.nodes.tag.Tag):
		return get_text(code.contents)
	if isinstance(code, mwparserfromhell.nodes.comment.Comment):
		return ""
	if isinstance(code, str):
		return code
	raise Exception(f"get_text not implemented for {type(code)}")


# https://gist.github.com/wassname/1393c4a57cfcbf03641dbc31886123b8
valid_filename_chars = f"-.() {string.ascii_letters}{string.digits}"

def clean_filename(filename, whitelist=valid_filename_chars):
	name, *ext = filename.split(".", 1)
	ext = ext[0] if ext else None

	# Keep only valid ascii chars.
	cleaned_filename = unicodedata.normalize("NFKD", name).encode("ASCII", "ignore").decode()

	# Keep only whitelisted chars.
	cleaned_filename = "".join(c for c in cleaned_filename if c in whitelist)

	# Truncate to Windows max length.
	target_len = 255
	if ext is not None:
		target_len -= len(ext) + 1

	cleaned_filename = cleaned_filename[:target_len]

	if ext is not None:
		return f"{cleaned_filename}.{ext}"
	return cleaned_filename
