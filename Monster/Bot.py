import time

import mwclient

from semigration.section import URL_WIKI_BASE, URL_WIKI_PATH


class Bot(object):

	def __init__(self, USERNAME, PASSWORD):
		self.session = mwclient.Site(URL_WIKI_BASE, URL_WIKI_PATH)
		self.session.login(USERNAME, PASSWORD)
		print("[BOT] Successfully logged in")

	def edit_and_save(self, page_name, wikitext):
		page = self.session.Pages[page_name]

		page.save(str(wikitext), summary='Semanticfied monster. Please check my work!')
		print("[BOT] Saved monster %s. Sleeping for 5 seconds\n===\n" % page_name)
		time.sleep(5)
		page.purge()

	def move_family(self, page_name):
		old_page = self.session.Pages[page_name]
		new_page = self.session.Pages[page_name + " (Family)"]

		new_page.save(old_page.text(), summary='Moved to family page before processing monsters')
		print("[BOT] Moved to new family page. %s Sleeping for 5 seconds\n===\n" % (page_name + " (Family)"))
		time.sleep(5)


###############
# Checks to see if the current family is an actual monster.
#     For example, if current_family is "Mimic" and "Mimic" exists as monster, then we need to stop script
#     and tell user to move pages. the family page should be named "Mimic (Family)"
# Returns True if there is a possible match
###############
def check_matching_name(current_family):
	site = mwclient.Site(URL_WIKI_BASE, URL_WIKI_PATH)
	text = site.pages[current_family].resolve_redirect().text()
	if "{{DataMonster{0}|format".format(current_family) in text:
		print("Possible monster that exists under {0} family".format(current_family))
		return True
	result = site.api("query", titles="Template:DataMonster{0}".format(current_family))
	for key in result['query']['pages'].keys():
		if key != '-1':
			print("Possible monster that exists under {0} family".format(current_family))
			return True

	return False
