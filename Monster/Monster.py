# whocontributes 07/04/2019
import difflib
import re
import webbrowser

import clipboard
import mwclient
import mwparserfromhell

from Monster_Globals import SKILL_BLACKLIST, VALID_SKILLS, CAPITIAL_EACH_WORD, FAMILY_PAGES_LIST

import semigration
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

# https://stackoverflow.com/a/46516776
def try_or(fn, default):
	try:
		return fn()
	except:
		return default


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
# Processes the parameters, Page-> Family, Skills, CP, Capitals, FieldBox or Mainstream
###############
def process_params_pages_skills_cp_capital_fieldboss_mainstream_section(wikicode, monster_type, section):
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
		elif "FieldBoss" in param.name or "Mainstream" in param.name:
			params_to_remove.append(param)
			if param.value.strip().lower() == "y" or param.value.strip().lower() == "yes":
				wikicode.add("SectionType", str(param.name))  # set FieldBoss and Mainstream to be part of SectionType.
		elif param.name == "Aggro":
			if param.value.strip().lower() == "y" or param.value.strip().lower() == "yes":
				param.value = "true\n"  # set aggro to true
			else:
				param.value = "false\n"

	for param in params_to_remove:
		params_list.remove(param)  # remove since we are going for list approach on skills
	wikicode.add("Type", monster_type + "\n")
	wikicode.add("Section", section + "\n")
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


###############
# Manually adds data for {{SemanticMonsterDifficultyData template
###############
def make_monster_difficulty(wikicode, monster_type):
	difficulty_template = mwparserfromhell.parse("{{SemanticMonsterDifficultyData\n}}").filter_templates()[0]
	if monster_type == "Normal":
		dungeon = try_or(lambda: wikicode.get("DungeonLocations").value, "")
		field = try_or(lambda: wikicode.get("FieldLocations").value, "")

		difficulty_template.add("Locations", str(dungeon).replace("*None", "") + str(field).replace("*None", "") + "\n")

		difficulty_template.add("Difficulty", "\n")

		# first, move all values to difficulty_template
		difficulty_template.add("HP", try_or(lambda: wikicode.get("HP").value, "\n"))
		difficulty_template.add("CP", try_or(lambda: wikicode.get("CP").value, "\n"))
		difficulty_template.add("Defense", try_or(lambda: wikicode.get("Defense").value, "\n"))
		difficulty_template.add("Protection", try_or(lambda: wikicode.get("Protection").value, "\n"))
		difficulty_template.add("MeleeDamage", try_or(lambda: wikicode.get("MeleeDamage").value, "\n"))
		difficulty_template.add("RangedDamage", try_or(lambda: wikicode.get("RangedDamage").value, "\n"))

		difficulty_template.add("MonsterCrit", try_or(lambda: wikicode.get("MonsterCrit").value, "\n"))
		difficulty_template.add("EXP", try_or(lambda: wikicode.get("EXP").value, "\n"))
		difficulty_template.add("Gold", try_or(lambda: wikicode.get("Gold").value, "\n"))
		difficulty_template.add("DropEquip", try_or(lambda: wikicode.get("DropEquip").value, "\n"))
		difficulty_template.add("DropMisc", try_or(lambda: wikicode.get("DropMisc").value, "\n"))

		# Then remove original values
		try_or(lambda: wikicode.remove("HP"), "")
		try_or(lambda: wikicode.remove("CP"), "")
		try_or(lambda: wikicode.remove("Defense"), "")
		try_or(lambda: wikicode.remove("Protection"), "")
		try_or(lambda: wikicode.remove("MeleeDamage"), "")
		try_or(lambda: wikicode.remove("RangedDamage"), "")

		try_or(lambda: wikicode.remove("MonsterCrit"), "")
		try_or(lambda: wikicode.remove("EXP"), "")
		try_or(lambda: wikicode.remove("Gold"), "")
		try_or(lambda: wikicode.remove("DropEquip"), "")
		try_or(lambda: wikicode.remove("DropMisc"), "")

		try_or(lambda: wikicode.remove("DungeonLocations"), "")
		try_or(lambda: wikicode.remove("FieldLocations"), "")

	if monster_type == "Shadow":
		wikicode, difficulty_template = process_params_shadow(wikicode)
	return mwparserfromhell.parse(
		re.sub(r'[\n]{2,}', '\n', str(wikicode)) + "<nowiki/>\n" + re.sub(r'[\n]{2,}', '\n', str(difficulty_template)))


###############
# Manually adds data for {{SemanticMonsterDifficultyData template for shadow monsters
###############
def process_params_shadow(wikicode):
	difficulty_total = ""
	params_list = wikicode.params

	for param in params_list:
		if "Mission" in param.name:  # change Mission to MissionsList
			param.name = "MissionsList"
		elif "AllDropMisc" in param.name:
			param.name = "DropMiscCommon"
		elif "AllDropEquip" in param.name:
			param.name = "DropEquipCommon"

	for diff in ["Basic", "Intermediate", "Advanced", "Hard", "Elite"]:
		difficulty_template = mwparserfromhell.parse("{{SemanticMonsterDifficultyData\n}}").filter_templates()[0]

		difficulty_template.add("Difficulty", diff + "\n")

		# first, move all values to difficulty_template
		difficulty_template.add(diff + "HP", try_or(lambda: wikicode.get(diff + "HP").value, "\n"))
		difficulty_template.add(diff + "CP", try_or(lambda: wikicode.get(diff + "CP").value, "\n"))
		difficulty_template.add(diff + "Defense", try_or(lambda: wikicode.get(diff + "Defense").value, "\n"))
		difficulty_template.add(diff + "Protection", try_or(lambda: wikicode.get(diff + "Protection").value, "\n"))
		difficulty_template.add(diff + "MeleeDamage", try_or(lambda: wikicode.get(diff + "MeleeDamage").value, "\n"))
		difficulty_template.add(diff + "RangedDamage", try_or(lambda: wikicode.get(diff + "RangedDamage").value, "\n"))

		difficulty_template.add(diff + "Crit", try_or(lambda: wikicode.get(diff + "Crit").value, "\n"))
		difficulty_template.add(diff + "EXP", try_or(lambda: wikicode.get(diff + "EXP").value, "\n"))
		difficulty_template.add(diff + "Gold", try_or(lambda: wikicode.get(diff + "Gold").value, "\n"))
		difficulty_template.add(diff + "DropEquip", try_or(lambda: wikicode.get(diff + "DropEquip").value, "\n"))
		difficulty_template.add(diff + "DropMisc", try_or(lambda: wikicode.get(diff + "DropMisc").value, "\n"))

		# Then remove original values
		try_or(lambda: wikicode.remove(diff + "HP"), "")
		try_or(lambda: wikicode.remove(diff + "CP"), "")
		try_or(lambda: wikicode.remove(diff + "Defense"), "")
		try_or(lambda: wikicode.remove(diff + "Protection"), "")
		try_or(lambda: wikicode.remove(diff + "MeleeDamage"), "")
		try_or(lambda: wikicode.remove(diff + "RangedDamage"), "")

		try_or(lambda: wikicode.remove(diff + "Crit"), "")
		try_or(lambda: wikicode.remove(diff + "EXP"), "")
		try_or(lambda: wikicode.remove(diff + "Gold"), "")
		try_or(lambda: wikicode.remove(diff + "DropEquip"), "")
		try_or(lambda: wikicode.remove(diff + "DropMisc"), "")
		difficulty_total = difficulty_total + str(difficulty_template) + "<nowiki/>\n"
	return wikicode, difficulty_total

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

	print("Wrote data")


def preprocess_pages():
	# for each family, get the templates used.

	for current_family in FAMILY_PAGES_LIST:
		current_page = semigration.parse(current_family)
		for key, value in current_page.headers.items():
			section = key
			if "DataMonster" in str(value.templates):  # ignore sections without DataMonster "general information"
				for item in value.templates:
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
						monster_type = "Baltane"
					elif "StyleShadowMonster" in str(item['format']):
						monster_type = "Theater"
					elif "Raid Dungeon Monster" in str(item["format"]):
						monster_type = "Raid"

					current_monster_name = str(item.name).replace("DataMonster", "")
					current_data_monster_templates_list = extract_templates("Template:" + str(item.name))

					param_done_wikicode = ""
					indexes_to_delete = []
					# Now we search for the {{{format}}} template
					for i, wikicode in enumerate(current_data_monster_templates_list):
						if "{{{format" in str(wikicode.name):
							orig_wikicode = str(wikicode)
							param_done_wikicode = process_params_pages_skills_cp_capital_fieldboss_mainstream_section(
								wikicode, monster_type, section)
						else:
							indexes_to_delete.append(i)

					for idx in indexes_to_delete:  # remove any non {{{format from list
						del current_data_monster_templates_list[idx]

					if param_done_wikicode != "":
						wikicode_with_monster_difficulty = make_monster_difficulty(param_done_wikicode, monster_type)
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


def main():
	preprocess_pages()


# upload_listdir("output")


if __name__ == "__main__":
	import os

	if not os.path.isdir("output"):
		os.mkdir("output")  # Save files to upload later
	main()
