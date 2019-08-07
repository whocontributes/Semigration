# whocontributes 07/04/2019
import difflib
import getpass
import re
import webbrowser
import clipboard
import mwclient
import mwparserfromhell
import Bot

from Monster_Globals import SKILL_BLACKLIST, VALID_SKILLS, CAPITIAL_EACH_WORD, FAMILY_PAGES_LIST, BALTANE_MISSIONS, \
	NUMERICAL_VALUES, AGGRO_RANGE, AGGRO_SPEED, SPEED, THEATRE_MISSIONS, MULTI_AGGRO, ELEMENT
from Monster_Params_Parser import make_monster_difficulty, try_or

import semigration
from semigration.section import URL_WIKI_BASE, URL_WIKI_PATH
from semigration.upload import URL_EDIT

warning_text = ""  # any text that needs to be sent to the user for review. For example, "old exp was 165-225. please double check this."

AUTO_UPLOAD = False
BOT_OBJ = None


# Writing down implementation steps so I don't forget
# main()
#   a. Ask user if they want to auto upload page using API
#      1. Ask user for credentials to wiki.
#   b. call process_family()
#      1. for each family, get templates used in that page.
#      2. for each template
#         i. If "DataMonster" is in this template, then continue
#      2.1. call process_page()
#         i. Determine the type of monster, such as Normal/Shadow/Sidhe
#         ii. Call extract_templates() on Template:DataMonster<monster name>
#            c.1. Add extra checks for type of mosnter
#         iii. Inside this DataMonster, find the template with {{{format since the first is usually {{Usage}}
#            d.1. saves the indexes to delete if it does not have {{{format
#         iv. Call process_common_params()
#             Read the if else statements in this function. Pretty much converts parameters to new semantic style
#         v. Call make_monster_difficulty()
#             This makes the {{SemanticMonsterDifficultyData rows
#         vi. Call get_ready_wikicode()
#             This does some minor string replace, prepending and appending. Does not edit the parameters
#         vii. Call write_files_or_upload()
#             Ask the user if they want to upload code to wiki or save to file
#             If global AUTO_UPLOAD is set to true, this will not prompt the user.
#         viii. If AUTO_UPLOAD is true, script will also auto update family pages to semantic calls
#


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
		text = site.pages[page].resolve_redirect().text()

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
# From the gold value, try to split using dash and return min and max. If failed, set to "\n" for unknown
###############
def convert_gold(param_name, value):
	global warning_text
	min = "\n"
	max = "\n"
	value = value.replace('~', '-')
	gold_list = value.split("-")
	if len(gold_list) == 2:
		min = try_or(lambda: int(gold_list[0].replace(',', '')), "\n")
		max = try_or(lambda: int(gold_list[1].replace(',', '')), "\n")
	else:
		min = try_or(lambda: int(gold_list[0].replace('+', '').replace(',', '')), "\n")
	if min == "\n" or max == "\n":
		warning_text = warning_text + "'''When importing data, old parameter [{0}] was '{1}'. Please manually check output'''<br>".format(
			param_name, value.strip())
	return min, max


NUMBERS_ONLY = re.compile(r'[^0-9.]')
CAMEL_CONVERT = re.compile(r"([a-z])([A-Z])")


###############
# From input wikicode, find all passive defenses
# If there is a letter, or value above 3, convert using formula   A-F=1   2-9=2   1=3
def convert_passive_def(wikicode):
	HS = try_or(lambda: wikicode.get("SkillHeavyStander").value.strip(), "0")
	MD = try_or(lambda: wikicode.get("SkillManaDeflector").value.strip(), "0")
	NS = try_or(lambda: wikicode.get("SkillNaturalShield").value.strip(), "0")
	bool_convert = False

	if HS.isalpha() or len(HS) == 0 or MD.isalpha() or len(MD) == 0 or NS.isalpha() or len(
			NS) == 0:  # if there is A-F. len == 0 is for empty string
		bool_convert = True
	else:
		if (HS.isdigit() and int(HS) > 3) or (MD.isdigit() and int(MD) > 3) or (
				NS.isdigit() and int(NS) > 3):  # if there is 4-9
			bool_convert = True

	try_or(lambda: wikicode.remove("SkillHeavyStander"), "")
	try_or(lambda: wikicode.remove("SkillManaDeflector"), "")
	try_or(lambda: wikicode.remove("SkillNaturalShield"), "")

	if bool_convert:
		if len(HS) != 0:  # Add values if there is NOT an empty string
			if HS.isalpha():  # A-F is 1
				wikicode.add("SkillHeavyStander", "1")
			else:
				if int(HS) > 1:  # 2-9 is 2
					wikicode.add("SkillHeavyStander", "2")
				elif int(HS) == 1:
					wikicode.add("SkillHeavyStander",
								 "3")  # rank 1 is level 3. If value is 0, monster does not have def

		if len(MD) != 0:  # Add values if there is NOT an empty string
			if MD.isalpha():  # A-F is 1
				wikicode.add("SkillManaDeflector", "1")
			else:
				if int(MD) > 1:  # 2-9 is 2
					wikicode.add("SkillManaDeflector", "2")
				elif int(MD) == 1:
					wikicode.add("SkillManaDeflector",
								 "3")  # rank 1 is level 3. If value is 0, monster does not have def

		if len(NS) != 0:  # Add values if there is NOT an empty string
			if NS.isalpha():  # A-F is 1
				wikicode.add("SkillNaturalShield", "1")
			else:
				if int(NS) > 1:  # 2-9 is 2
					wikicode.add("SkillNaturalShield", "2")
				elif int(NS) == 1:
					wikicode.add("SkillNaturalShield",
								 "3")  # rank 1 is level 3. If value is 0, monster does not have def
	else:  # reuse values
		# if we cannot convert to int, just set to 1. letters have already been processed so this covers special characters
		HS = try_or(lambda: int(HS), "1")
		MD = try_or(lambda: int(MD), "1")
		NS = try_or(lambda: int(NS), "1")
		if int(HS) != 0: wikicode.add("SkillHeavyStander", HS)
		if int(MD) != 0: wikicode.add("SkillManaDeflector", MD)
		if int(NS) != 0: wikicode.add("SkillNaturalShield", NS)

	return wikicode


###############
# Attempts to get the file extension of the monster. Returns "\n" if not found
###############
def try_get_file_ext(monster_name):
	site = mwclient.Site(URL_WIKI_BASE, URL_WIKI_PATH)

	return_me = "\n"
	for ext in ["jpg", "png"]:  # Old pages have jpg, so check that first
		filename = "File:{0}.{1}".format(monster_name.strip(), ext)
		result = site.api("query", titles=filename)
		for key in result['query']['pages'].keys():
			if key != '-1':
				return_me = ext + "\n"

	return return_me


###############
# Processes the parameters that are common to all
###############
def process_common_params(wikicode, monster_type, section, current_family):
	global warning_text

	try_or(lambda: wikicode.remove("DropsOverflow"), "")  # no idea what this parameter is used for
	try_or(lambda: wikicode.remove("LocationOverflow"), "")  # no idea what this parameter is used for
	fileExt = try_or(lambda: wikicode.get("Ext").value, None)
	if fileExt is None:
		fileExt = try_get_file_ext(try_or(lambda: wikicode.get("Name").value, None))
		wikicode.add("Ext", fileExt)
		warning_text = warning_text + "'''When importing data, file extension was not set (|Ext=). We have tried to find the file. Please check output'''<br>"

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
			list_value_split = str(param.value).replace('-', ' ').replace('(', ' ').replace('~',
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
			param.value = current_family + "\n"
		elif "PartyHeal" in param.name:
			skills_list.append("Party Healing")
			params_to_remove.append(param)
			warning_text = warning_text + "'''When importing data, partyHeal was found'''<br>"
		elif "Skill" in param.name and ("AdvancedHeavyStander" in param.name or not any(
				name in param.name for name in SKILL_BLACKLIST)):  # push skills into a list
			if param.value.strip().lower() == "y":
				just_skill = str(param.name).replace("Skill", "")
				if just_skill == "Counter":
					just_skill = "Counterattack"  # goes to lance counter if we try closest match
				if just_skill == "Flight":
					just_skill = "Flight (Monster Skill)"
				if just_skill == "DragonDashAttack":
					just_skill = "Smack"
				just_skill = CAMEL_CONVERT.sub("\g<1> \g<2>", just_skill)
				closest_skill_list = difflib.get_close_matches(just_skill, VALID_SKILLS)
				if len(closest_skill_list) > 0:
					skills_list.append(closest_skill_list[0])
				else:
					warning_text = warning_text + "'''When importing data, skill [{0}] was not found'''<br>".format(
						just_skill)
					skills_list.append(just_skill)

			params_to_remove.append(
				param)  # add to separate list  since deleting now will remove a node and change indexes. Messes up for loop

			if "AdvancedHeavyStander" in param.name:
				warning_text = warning_text + "''Manually add Adv heavy stander to skill list'''<br>"
		elif param.name == "Speed":
			if str(param.value).strip() == "Average" or str(param.value).strip() == "Normal":
				param.value = "Medium"
			if str(param.value).strip() == "Above Average":
				param.value = "Fast"
			param = get_closest(param, SPEED)
		elif param.name == "AggroSpeed":
			if str(param.value).strip() == "Average" or str(param.value).strip() == "Normal":
				param.value = "Medium"
			if str(param.value).strip() == "Small":
				param.value = "Slow"
			if str(param.value).strip() == "Far" or str(param.value).strip() == "Above Average":
				param.value = "Fast"
			param = get_closest(param, AGGRO_SPEED)

		elif param.name == "AggroRange":
			if str(param.value).strip() == "Average" or str(param.value).strip() == "Normal":
				param.value = "Medium"
			if str(param.value).strip() == "Unlimited" or str(param.value).strip() == "Instant":
				param.value = "Extremely Far"
			if str(param.value).strip() == "Wide":
				param.value = "Far"
			if str(param.value).strip() == "Short":
				param.value = "Small"
			param = get_closest(param, AGGRO_RANGE)

		elif param.name == "MultiAggro":
			param = get_closest(param, MULTI_AGGRO)

		elif "CP" in param.name:  # If CP has a "?", convert to empty string
			if param.value.strip().lower() == "?":
				param.value = "\n"
		elif "FieldBoss" in param.name or "Mainstream" in param.name:
			param = yes_no(param)
		elif param.name == "Aggro":
			param = yes_no(param)
		elif param.name == "Element":
			if param.value.strip().lower() == "unknown":
				param.value = "\n"

			param = get_closest(param, ELEMENT)

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

	if monster_type == "GM":
		wikicode.add("Type", "Shadow\n")
	else:
		wikicode.add("Type", monster_type + "\n")
	wikicode.add("Section", section + "\n")
	wikicode.add("Skills", ",".join(skills_list))
	if len(skills_list) ==0:
		warning_text = warning_text + "''Skill list is empty'''<br>"

	return wikicode


###############
# Performs string replacement and appends text
#    to make page ready for new semantic form
###############
def get_ready_wikicode(wikicode):
	# wikicode = wikicode.replace("{{{format}}}", "SemanticMonsterData")
	if AUTO_UPLOAD:  # auto upload does not need warning text. just print
		string = str(wikicode) + "{{RenderSemanticMonster}}<nowiki/>\n"
		monster_name = try_or(lambda: wikicode.filter_templates()[0].get("Name"), "\n")
		print("[REVIEW WARNING BEFORE UPLOAD] {0}{1}".format(monster_name, warning_text.replace("<br>", "\n   ")))
		input("Press enter to continue...")

	else:
		string = str(wikicode) + "{{RenderSemanticMonster}}<nowiki/>\n" + warning_text
	i = string.index('\n')
	new_string = "{{SemanticMonsterData" + string[i:]
	return mwparserfromhell.parse(new_string)


def write_files_or_upload(current_monster_name, ready_wikicode):
	if AUTO_UPLOAD:
		BOT_OBJ.edit_and_save(current_monster_name, ready_wikicode)
	else:
		value = ""
		while value == "":
			value = input("Do you want to upload now? [{0}](y/n) ".format(current_monster_name))
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


def process_family_gm():
	from Monster_Globals import GM_LIST
	global warning_text
	current_section_id = 0  # replace entire page
	section = ""
	# for each family, get the templates used.
	for i, current_family in enumerate(GM_LIST):
		made_changes = False
		# Bot.check_matching_name(current_family)
		current_page = semigration.parse(current_family)
		sections_list = []
		if "DataMonster" in str(current_page.templates):  # ignore sections without DataMonster "general information"
			for item in current_page.templates:
				warning_text = ""  # reset before process monster

				if "DataMonster" in str(item):  # again ignore non DataMonster templates, like enchants
					find_type_gm(current_family, item, section)
					made_changes = True

		if AUTO_UPLOAD and made_changes:
			print("Finished family [{0}].({1}/{2})".format(current_family, i, len(GM_LIST)))
			input("Waiting for user")


def process_family():
	global warning_text
	# for each family, get the templates used.
	for i, current_family in enumerate(FAMILY_PAGES_LIST):
		made_changes = False
		# Bot.check_matching_name(current_family)
		current_page = semigration.parse(current_family)
		sections_list = []
		current_section_id = 0
		for key, value in current_page.headers.items():
			section = key
			current_section_id = current_section_id + 1
			if "DataMonster" in str(value.templates):  # ignore sections without DataMonster "general information"
				ret = Bot.check_matching_name(
					current_family)  # moved check down here. Prevents checking already processed families
				if AUTO_UPLOAD and ret:
					user_in = input("Do you want to auto move? [{0}](y/n) ".format(current_family))
					if user_in.lower() == "y":
						BOT_OBJ.move_family(current_family)
						print("Please update the monster globals")

				if ret:  # no auto upload, so exit
					exit(1)

				for item in value.templates:
					warning_text = ""  # reset before process monster

					if "DataMonster" in str(item):  # again ignore non DataMonster templates, like enchants
						find_type(current_family, item, section)
						made_changes = True
				if made_changes:
					sections_list.append({"name": section, "id": current_section_id})

		if AUTO_UPLOAD and made_changes:
			BOT_OBJ.update_family_to_semantic(current_family, sections_list)

		if AUTO_UPLOAD and made_changes:
			input("Finished family [{0}].({1}/{2}) Waiting for user".format(current_family, i, len(FAMILY_PAGES_LIST)))


def find_type_gm(current_family, item, section):
	monster_type = "GM"
	if "{{PAGENAME}}" in str(item.name):
		item.name = str(item.name).replace("{{PAGENAME}}", current_family)
	current_monster_name = str(item.name).replace("DataMonster", "")

	current_data_monster_templates_list = extract_templates("Template:" + str(item.name))

	process_page(current_data_monster_templates_list, monster_type, section, current_family, current_monster_name)


def find_type(current_family, item, section):
	monster_type = "Normal"
	if 'format' not in item:
		item['format'] = item['1']
	if "StyleShadowMonster" in str(item['format']):
		monster_type = "Shadow"
	elif "StyleLordMonster" in str(item['format']):
		monster_type = "Lord"
	elif "StyleFinnachaidMonster" in str(item['format']):
		monster_type = "Sidhe"
	elif "StyleBandit" in str(item['format']):
		monster_type = "Bandit"
	elif "StyleAlban Dungeon Monster" in str(item['format']):
		monster_type = "Alban"
	elif "Raid Dungeon Monster" in str(item["format"]):
		monster_type = "Raid"
	current_monster_name = str(item.name).replace("DataMonster", "")
	current_data_monster_templates_list = extract_templates("Template:" + str(item.name))
	if monster_type == "Shadow" and any(
			"|Lord" + stat in str(current_data_monster_templates_list) for stat in
			NUMERICAL_VALUES):
		print("[WARNING] Lord monster detected. Please confirm output.")
		monster_type = "Lord"
	elif monster_type == "Shadow" and any(
			balt_mission in str(current_data_monster_templates_list) for balt_mission in
			BALTANE_MISSIONS):
		print("[WARNING] Baltane monster detected. Please confirm output.")
		monster_type = "Baltane"
	elif monster_type == "Shadow" and any(
			theatre in str(current_data_monster_templates_list) for theatre in
			THEATRE_MISSIONS):
		print("[WARNING] Theatre monster detected. Please confirm output.")
		monster_type = "Theatre"
	elif "Finnachaid" in str(current_data_monster_templates_list):
		print("[WARNING] Sidhe Finnachaid monster detected. Please confirm output.")
		monster_type = "Sidhe"
	elif "Alban" in str(current_data_monster_templates_list):
		print("[WARNING] Alban monster detected. Please confirm output.")
		monster_type = "Alban"
	elif monster_type == "Shadow" and "[[Grandmaster Mission]]" in str(current_data_monster_templates_list):
		print("[WARNING] GM monster detected. Please confirm output.")
		monster_type = "GM"

	process_page(current_data_monster_templates_list, monster_type, section, current_family, current_monster_name)


def process_page(current_data_monster_templates_list, monster_type, section, current_family, current_monster_name):
	param_done_wikicode = ""
	indexes_to_delete = []
	# Now we search for the {{{format}}} template
	for i, wikicode in enumerate(current_data_monster_templates_list):
		if "{{{format" in str(wikicode.name):
			param_done_wikicode = process_common_params(
				wikicode, monster_type, section, current_family)
		elif "times" in str(wikicode.name):
			pass  # keep template times
		else:
			indexes_to_delete.append(i)
	for idx in reversed(indexes_to_delete):  # remove any non {{{format from list
		del current_data_monster_templates_list[idx]
	if param_done_wikicode != "":
		wikicode_with_monster_difficulty = make_monster_difficulty(param_done_wikicode,
																   monster_type)
		ready_wikicode = get_ready_wikicode(wikicode_with_monster_difficulty)

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


###############
# 1. Loop through all families
# 2. if monster is detected, mark boolean to true
# 3. Counter number of DataMonster.
#    3.1 If number is =1, print out will not move family. append to separate list
#    3.2 If number is >1, move to family page
# 4. when done print out new list(s) so user can update globals
# 5. exit program
###############
def ask_auto_move():
	global FAMILY_PAGES_LIST
	FAMILY_PAGES_LIST = sorted(FAMILY_PAGES_LIST)
	value = input("Do you want to auto move families? (y/n) ")
	if value.lower() == "y":
		USERNAME = input("What is your mabi wiki username? ")
		PASSWORD = getpass.getpass("What is your mabi wiki password? ")
		bot = Bot.Bot(USERNAME, PASSWORD)
		new_family_list = []
		moved_list = []
		one_monster_page_list = []

		for current_family in FAMILY_PAGES_LIST:
			print("[AUTO MOVE] Checking {0}".format(current_family))
			current_page = semigration.parse(current_family)
			need_to_move = False
			current_family_count = 0
			for key, value in current_page.headers.items():
				section = key
				if "DataMonster" in str(value.templates):  # ignore sections without DataMonster "general information"
					ret = Bot.check_matching_name(
						current_family)

					if ret or need_to_move:
						need_to_move = True
						for item in value.templates:

							if "DataMonster" in str(item):  # again ignore non DataMonster templates, like enchants
								current_family_count = current_family_count + 1
			if need_to_move:
				if current_family_count == 1:
					print(" [WILL NOT MOVE] {0}, since there is only one monster".format(current_family))
					one_monster_page_list.append(current_family)
				if current_family_count > 1:
					bot.move_family(current_family)
					# print("   [DRY RUN] Moving {0}".format(current_family))
					moved_list.append(current_family)
					current_family = current_family + " (Family)"
			if current_family_count != 1:  # those with one have a different list
				new_family_list.append(current_family)

		print("new list = " + str(new_family_list))
		print("moved list = " + str(moved_list))
		print("one monster list = " + str(one_monster_page_list))
		print("Please update globals")
		print("We found {0} possible new family pages".format(len(moved_list)))
		exit(1)


def ask_auto_upload():
	global AUTO_UPLOAD, BOT_OBJ

	value = input("Do you want to auto upload? (y/n) ")
	if value.lower() == "y":
		AUTO_UPLOAD = True
		USERNAME = input("What is your mabi wiki username? ")
		PASSWORD = getpass.getpass("What is your mabi wiki password? ")
		BOT_OBJ = Bot.Bot(USERNAME, PASSWORD)


def main():
	# ask_auto_move()
	ask_auto_upload()
	process_family()
	# process_family_gm()


# upload_listdir("output")


if __name__ == "__main__":
	import os

	if not os.path.isdir("output"):
		os.mkdir("output")  # Save files to upload later
	main()
