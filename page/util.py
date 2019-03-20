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
	if isinstance(code, str):
		return code
	raise Exception(f"get_text not implemented for {type(code)}")