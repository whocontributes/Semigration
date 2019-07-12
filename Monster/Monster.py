# whocontributes 07/04/2019
import difflib
import re
import webbrowser

import clipboard
import mwclient
import mwparserfromhell

from Monster_Globals import SKILL_BLACKLIST, VALID_SKILLS, CAPITIAL_EACH_WORD, FAMILY_PAGES_LIST, BALTANE_MISSIONS, \
	NUMERICAL_VALUES, AGGRO_RANGE, AGGRO_SPEED, SPEED
from Monster_Params_Parser import make_monster_difficulty, try_or

import semigration
from semigration.section import URL_WIKI_BASE, URL_WIKI_PATH
from semigration.upload import URL_EDIT

warning_text = ""  # any text that needs to be sent to the user for review. For example, "old exp was 165-225. please double check this."


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
# Takes in a param from wikicode and a list.
# Using difflib, find the closest value from list and return the param
###############
def get_closest(param, look_in_list):
	global warning_text
	closest_range_list = difflib.get_close_matches(str(param.value).strip(), look_in_list)
	if len(closest_range_list) >= 1:
		param.value = closest_range_list[0] + "\n"
	else:
		warning_text = warning_text + "'''When importing data, old parameter [{0}] was '{1}'. Please check output.'''<br>".format(
			param.name, param.value.strip())
		param.value = "\n"  # could not find a value.
	return param


###############
# Using .lower() check if param.value is 'y' or 'yes'. Return param with new 'Yes' or 'No'
###############
def yes_no(param):
	if param.value.strip().lower() == "y" or param.value.strip().lower() == "yes":
		param.value = "Yes\n"  # set aggro to true
	else:
		param.value = "No\n"
	return param


###############
# From the gold value, try to split using dash and return min and max. If failed, set to 0.
###############
def convert_gold(param_name, value):
	global warning_text
	min = 0
	max = 0
	gold_list = value.split("-")
	if len(gold_list) == 2:
		min = try_or(lambda: int(gold_list[0].replace(',', '')), 0)
		max = try_or(lambda: int(gold_list[1].replace(',', '')), 0)
	else:
		min = try_or(lambda: int(gold_list[0].replace('+', '').replace(',', '')), 0)
	if min == 0 or max == 0:
		warning_text = warning_text + "'''When importing data, old parameter [{0}] was '{1}'. Please manually check output'''<br>".format(
			param_name, value.strip())
	return min, max


NUMBERS_ONLY = re.compile(r'[^0-9]')


###############
# From input wikicode, find all passive defenses
# If there is a letter, or value above 3, convert using formula   A-F=1   2-9=2   1=3
def convert_passive_def(wikicode):
	HS = try_or(lambda: wikicode.get("SkillHeavyStander").value.strip(), "0")
	MD = try_or(lambda: wikicode.get("SkillManaDeflector").value.strip(), "0")
	NS = try_or(lambda: wikicode.get("SkillNaturalShield").value.strip(), "0")
	bool_convert = False

	if HS.isalpha() or MD.isalpha() or NS.isalpha():  # if there is A-F
		bool_convert = True
	else:
		if int(HS) > 3 or int(MD) > 3 or int(NS) > 3:  # if there is 4-9
			bool_convert = True

	try_or(lambda: wikicode.remove("SkillHeavyStander"), "")
	try_or(lambda: wikicode.remove("SkillManaDeflector"), "")
	try_or(lambda: wikicode.remove("SkillNaturalShield"), "")

	if bool_convert:
		if HS.isalpha():  # A-F is 1
			wikicode.add("SkillHeavyStander", "1")
		else:
			if int(HS) > 1:  # 2-9 is 2
				wikicode.add("SkillHeavyStander", "2")
			elif int(HS) == 1:
				wikicode.add("SkillHeavyStander", "3")  # rank 1 is level 3. If value is 0, monster does not have def

		if MD.isalpha():  # A-F is 1
			wikicode.add("SkillManaDeflector", "1")
		else:
			if int(MD) > 1:  # 2-9 is 2
				wikicode.add("SkillManaDeflector", "2")
			elif int(MD) == 1:
				wikicode.add("SkillManaDeflector", "3")  # rank 1 is level 3. If value is 0, monster does not have def

		if NS.isalpha():  # A-F is 1
			wikicode.add("SkillNaturalShield", "1")
		else:
			if int(NS) > 1:  # 2-9 is 2
				wikicode.add("SkillNaturalShield", "2")
			elif int(NS) == 1:
				wikicode.add("SkillNaturalShield", "3")  # rank 1 is level 3. If value is 0, monster does not have def
	else:
		if int(HS) != 0: wikicode.add("SkillHeavyStander", HS)
		if int(MD) != 0: wikicode.add("SkillManaDeflector", MD)
		if int(NS) != 0: wikicode.add("SkillNaturalShield", NS)

	return wikicode


###############
# Processes the parameters,
# Page-> Family,
# Skills,
# CP,
# Capitals,
# FieldBox or Mainstream
# Aggro -> true or false
# Element: Unknown -> empty string
###############
def process_common_params(wikicode, monster_type, section):
	global warning_text

	try_or(lambda: wikicode.remove("DropsOverflow"), "")  # no idea what this parameter is used for
	try_or(lambda: wikicode.remove("LocationOverflow"), "")  # no idea what this parameter is used for
	fileExt = try_or(lambda: wikicode.get("Ext").value, None)
	if fileExt is None:
		warning_text = warning_text + "'''When importing data, file extension was not set (|Ext=). Please check output'''<br>"

	wikicode = convert_passive_def(wikicode)
	params_list = wikicode.params
	params_to_remove = []
	skills_list = []
	gold_to_push = {}

	for param in params_list:
		if any(name in param.name for name in CAPITIAL_EACH_WORD):  # Capitalize each word
			param.value = param.value.title() + "\n"
		if param.name != "SkillDefense" and any(name in param.name for name in
												NUMERICAL_VALUES):  # drop any non numerical values. Since skill and stats def is same, we need to remove that from check
			old_param_value = str(param.value)
			list_value_split = str(param.value).replace('.', ' ').replace('-', ' ').replace('(', ' ').replace('~',
																											  ' ').split()  # check for dashes, tildes,spaces
			if len(list_value_split) >= 2:
				param.value = NUMBERS_ONLY.sub('', str(list_value_split[0])) + "\n"
				warning_text = warning_text + "'''When importing data, old parameter [{0}] was '{1}'. It has been assigned to be '{2}'.'''<br>".format(
					param.name, old_param_value.strip(), param.value.strip())
			else:
				param.value = NUMBERS_ONLY.sub('', str(param.value)) + "\n"  # no dashes or tildes, so single value

		if "Page" in param.name:  # change Page to Family
			# param = mwparserfromhell.parse(param.replace("Page", "Family"))
			param.name = "Family"
		elif "Skill" in param.name and not any(
				name in param.name for name in SKILL_BLACKLIST):  # push skills into a list
			if param.value.strip().lower() == "y":
				just_skill = str(param.name).replace("Skill", "")
				if just_skill == "Counter":
					just_skill = "Counterattack"  # goes to lance counter if we try closest match
				if just_skill == "Flight":
					just_skill = "Flight (Monster Skill)"
				if just_skill == "DragonDashAttack":
					just_skill = "Smack"
				closest_skill_list = difflib.get_close_matches(just_skill, VALID_SKILLS)
				skills_list.append(closest_skill_list[0])

			params_to_remove.append(
				param)  # add to separate list  since deleting now will remove a node and change indexes. Messes up for loop
		elif param.name == "Speed":
			if str(param.value).strip() == "Average" or str(param.value).strip() == "Normal":
				param.value = "Medium"
			param = get_closest(param, SPEED)
		elif param.name == "AggroSpeed":
			if str(param.value).strip() == "Average" or str(param.value).strip() == "Normal":
				param.value = "Medium"
			if str(param.value).strip() == "Small":
				param.value = "Slow"
			param = get_closest(param, AGGRO_SPEED)

		elif param.name == "AggroRange":
			if str(param.value).strip() == "Average" or str(param.value).strip() == "Normal":
				param.value = "Medium"
			if str(param.value).strip() == "Wide":
				param.value = "Far"
			if str(param.value).strip() == "Short":
				param.value = "Small"
			param = get_closest(param, AGGRO_RANGE)

		elif "CP" in param.name:  # If CP has a "?", convert to empty string
			if param.value.strip().lower() == "?":
				param.value = "\n"
		elif "FieldBoss" in param.name or "Mainstream" in param.name:
			param = yes_no(param)
		elif param.name == "Aggro":
			param = yes_no(param)
		elif param.name == "Element":
			if param.value.strip().lower() == "Unknown":
				param.value = "\n"
		elif "Gold" in param.name and ("GoldMin" not in param.name and "GoldMax" not in param.name):
			params_to_remove.append(param)
			min, max = convert_gold(str(param.name), str(param.value))
			difficulty = str(param.name).replace("Gold", "")
			if difficulty == "":
				gold_to_push["GoldMin"] = min
				if max != 0: gold_to_push["GoldMax"] = max
			else:
				gold_to_push[difficulty + "GoldMin"] = min
				if max != 0: gold_to_push[difficulty + "GoldMax"] = max

	for param in params_to_remove:
		params_list.remove(param)  # remove since we are going for list approach on skills
	for key, value in gold_to_push.items():
		wikicode.add(key, value)

	wikicode.add("Type", monster_type + "\n")
	wikicode.add("Section", section + "\n")
	wikicode.add("Skills", ",".join(skills_list))

	return wikicode


###############
# Performs string replacement and appends text
#    to make page ready for new semantic form
###############
def get_ready_wikicode(wikicode, warning_text):
	# wikicode = wikicode.replace("{{{format}}}", "SemanticMonsterData")

	string = str(wikicode) + "{{RenderSemanticMonster}}<nowiki/>\n" + warning_text
	i = string.index('\n')
	new_string = "{{SemanticMonsterData" + string[i:]
	return mwparserfromhell.parse(new_string)


def write_files_or_upload(current_monster_name, ready_wikicode):
	value = ""
	while value == "":
		value = input("Do you want to upload now? [%s](y/n) " % current_monster_name)
	if value.lower() == "y":
		myupload(current_monster_name, str(ready_wikicode))

	else:
		write_files(current_monster_name, ready_wikicode)


###############
# write files for staging and reviewing
###############
def write_files(current_monster_name, ready_wikicode):
	with open("output/%s.new.txt" % current_monster_name, "w") as goodFile:
		goodFile.write(str(ready_wikicode))

	print("Wrote to file")

def preprocess_pages():
	global warning_text
	# for each family, get the templates used.

	for current_family in FAMILY_PAGES_LIST:
		current_page = semigration.parse(current_family)
		for key, value in current_page.headers.items():
			section = key
			if "DataMonster" in str(value.templates):  # ignore sections without DataMonster "general information"
				for item in value.templates:
					warning_text = ""  # reset before process monster

					if "DataMonster" in str(item):  # again ignore non DataMonster templates, like enchants
						monster_type = "Normal"
						if "StyleShadowMonster" in str(item['format']):
							monster_type = "Shadow"
						elif "StyleLordMonster" in str(item['format']):
							monster_type = "Lord"
						elif "StyleFinnachaidMonster" in str(item['format']):
							monster_type = "Sidhe"
						elif "StyleBandit" in str(item['format']):
							monster_type = "Bandit"
						elif "StyleAlban Dungeon Monster," in str(item['format']):
							monster_type = "Alban"
						elif "StyleShadowMonster" in str(item['format']):
							monster_type = "Theater"
						elif "Raid Dungeon Monster" in str(item["format"]):
							monster_type = "Raid"

						current_monster_name = str(item.name).replace("DataMonster", "")
						current_data_monster_templates_list = extract_templates("Template:" + str(item.name))

						if monster_type == "Shadow" and "Lord" in str(current_data_monster_templates_list):
							print("[WARNING] Lord monster detected. Please confirm output.")
							monster_type = "Lord"
						elif monster_type == "Shadow" and any(
								balt_mission in str(current_data_monster_templates_list) for balt_mission in
								BALTANE_MISSIONS):
							print("[WARNING] Baltane monster detected. Please confirm output.")
							monster_type = "Baltane"
						elif "Finnachaid" in str(current_data_monster_templates_list):
							print("[WARNING] Sidhe Finnachaid monster detected. Please confirm output.")
							monster_type = "Sidhe"

						param_done_wikicode = ""
						indexes_to_delete = []
						# Now we search for the {{{format}}} template
						for i, wikicode in enumerate(current_data_monster_templates_list):
							if "{{{format" in str(wikicode.name):
								param_done_wikicode = process_common_params(
									wikicode, monster_type, section)
							elif "times" in str(wikicode.name):
								pass # keep template times
							else:
								indexes_to_delete.append(i)

						for idx in indexes_to_delete:  # remove any non {{{format from list
							del current_data_monster_templates_list[idx]

						if param_done_wikicode != "":
							wikicode_with_monster_difficulty = make_monster_difficulty(param_done_wikicode,
																					   monster_type)
							ready_wikicode = get_ready_wikicode(wikicode_with_monster_difficulty, warning_text)

							write_files_or_upload(current_monster_name, ready_wikicode)


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
			if file.endswith('.new.txt'):
				process_file(directory + "/" + file, file.split(".")[0])

	print("d")


def main():
	preprocess_pages()


# upload_listdir("output")


if __name__ == "__main__":
	import os

	if not os.path.isdir("output"):
		os.mkdir("output")  # Save files to upload later
	main()
