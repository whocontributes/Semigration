# whocontributes 07/04/2019
import difflib
import webbrowser
from difflib import SequenceMatcher

import clipboard
import mwclient
import mwparserfromhell

from Monster_Globals import SKILL_BLACKLIST, VALID_SKILLS, CAPITIAL_EACH_WORD, FAMILY_PAGES_LIST
from semigration.section import URL_WIKI_BASE, URL_WIKI_PATH
from semigration.upload import URL_EDIT


# Writing down implementation steps so I don't forget
# main()
#   a. preprocess_pages()
#      1. for each family, get templates used in that page.
#      2. for each template
#         a. If "StyleMonster" is in this template, then continue
#         b. Call extract_templates() on Template:DataMonster<monster name>
#         c. Inside this DataMonster, find the template with {{{format since the first is usually {{Usage}}
#         d. Call process_params()
#             Read the if else statements in this function. Pretty much converts parameters to new semantic style
#         e. Call get_ready_wikicode()
#             This does some minor string replace, prepending and appending. Does not edit the parameters
#         f. Call write_files_or_upload()
#             Ask the user if they want to upload code to wiki or save to good/bad. Cutoff is 70% matching
#   b. upload_listdir("good") After reviewing the old and new, this function will loop through the good directory and upload to wiki
# https://stackoverflow.com/a/17388505
def similar(a, b):
	return SequenceMatcher(None, a, b).ratio()


def myupload(name, contents):
	clipboard.copy(contents)
	webbrowser.open(URL_EDIT.format(name=name))
	input("Press enter to continue...")


###############
# Returns a list of templates on a page
###############
def extract_templates(page=None, *, text=None):
	if text is None:
		site = mwclient.Site(URL_WIKI_BASE, URL_WIKI_PATH)
		text = site.pages[page].text()

	return mwparserfromhell.parse(text).filter_templates()


###############
# Processes the parameters in a page
###############
def process_params(wikicode):
	params_list = wikicode.params
	params_to_remove = []
	skills_list = []

	for param in params_list:
		if "Page" in param.name:  # change Page to Family
			# param = mwparserfromhell.parse(param.replace("Page", "Family"))
			param.name = "Family"
		elif "Skill" in param.name and not any(
				name in param.name for name in SKILL_BLACKLIST):  # push skills into a list
			if param.value.strip().lower() == "y":
				just_skill = str(param.name).replace("Skill", "")
				if just_skill == "Counter":
					just_skill = "Counterattack"  # goes to lance counter if we try closest match
				closest_skill_list = difflib.get_close_matches(just_skill, VALID_SKILLS)
				skills_list.append(closest_skill_list[0])

			params_to_remove.append(
				param)  # add to separate list  since deleting now will remove a node and change indexes. Messes up for loop
		elif "CP" in param.name:  # If CP has a "?", convert to empty string
			if param.value.strip().lower() == "?":
				param.value = "\n"
		elif any(name in param.name for name in CAPITIAL_EACH_WORD):  # Capitalize each word
			param.value = param.value.title()
		elif "FieldBoss" in param.name or "Mainstream" in param.name:  # set FieldBoss and Mainstream to "true" or "false"
			if param.value.strip().lower() == "y" or param.value.strip().lower() == "yes":
				param.value = "true\n"
			else:
				param.value = "false\n"

	for param in params_to_remove:
		params_list.remove(param)  # remove since we are going for list approach

	wikicode.add("Skills", ",".join(skills_list))
	return wikicode


###############
# Performs string replacement and appends text
#    to make page ready for new semantic form
###############
def get_ready_wikicode(wikicode):
	# wikicode = wikicode.replace("{{{format}}}", "SemanticMonsterData")

	string = str(wikicode) + "<nowiki/>\n{{RenderSemanticMonster}}<nowiki/>"
	i = string.index('\n')
	new_string = "{{SemanticMonsterData" + string[i:]
	return mwparserfromhell.parse(new_string)


def write_files_or_upload(current_monster_name, orig_wikicode, ready_wikicode):
	similar_value = similar(str(orig_wikicode), str(ready_wikicode))

	value = ""
	while value == "":
		value = input(
			"[%s] Similar value is %0.2f. Do you want to upload now? (y/n) " % (current_monster_name, similar_value))
	if value.lower() == "y":
		myupload(current_monster_name, str(ready_wikicode))

	else:
		write_files(current_monster_name, orig_wikicode, ready_wikicode, similar_value)


###############
# write files for staging and reviewing
###############
def write_files(current_monster_name, orig_wikicode, ready_wikicode, similar_value):
	status_out = "We have a %0.2f difference between old and new for %s" % (similar_value, current_monster_name)

	if similar_value > 0.7:
		with open("good/%s.old" % current_monster_name, "w") as goodFile:
			goodFile.write(str(orig_wikicode))
		with open("good/%s.new" % current_monster_name, "w") as goodFile:
			goodFile.write(str(ready_wikicode))
	else:
		status_out = "{BAD] " + status_out

		with open("bad/%s.old" % current_monster_name, "w") as goodFile:
			goodFile.write(str(orig_wikicode))
		with open("bad/%s.new" % current_monster_name, "w") as goodFile:
			goodFile.write(str(ready_wikicode))

	print(status_out)


def preprocess_pages():
	# for each family, get the templates used.

	for current_family in FAMILY_PAGES_LIST:
		current_page_templates_list = extract_templates(current_family)
		for item in current_page_templates_list:
			if "StyleMonster" in str(
					item.params):  # this file only processes normal monsters. Ignore Lord/Shadow mission/etc
				current_monster_name = str(item.name).replace("DataMonster", "")
				current_data_monster_templates_list = extract_templates("Template:" + str(item.name))

				# Now we search for the {{{format}}} template
				for wikicode in current_data_monster_templates_list:
					if "{{{format" in str(wikicode.name):
						orig_wikicode = str(wikicode)
						param_done_wikicode = process_params(wikicode)
						ready_wikicode = get_ready_wikicode(param_done_wikicode)

						write_files_or_upload(current_monster_name, orig_wikicode, ready_wikicode)


def process_file(filepath, page_name):
	page_content = ""
	with open(filepath, "r") as inFile:
		page_content = inFile.read()
	myupload(page_name, page_content)


###############
# Read through a directory get get all ".new" files
###############
def upload_listdir(directory):
	for root, dirs, files in os.walk(directory):
		for file in files:
			if file.endswith('.new'):
				process_file(directory + "/" + file, file.split(".")[0])

	print("d")


def main():
	preprocess_pages()
	upload_listdir("good")
	upload_listdir("bad")


if __name__ == "__main__":
	import os

	if not os.path.isdir("good"):
		os.mkdir("good")  # files that have a similar_value above 0.7. We should be able to upload
	if not os.path.isdir("bad"):
		os.mkdir("bad")  # files that are too different. Might need to check them
	main()
