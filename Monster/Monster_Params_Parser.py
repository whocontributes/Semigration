import re

import mwparserfromhell

NEW_LINES = re.compile(r'^[\n]{1,}$')


# https://stackoverflow.com/a/46516776
def try_or(fn, default):
	try:
		return fn()
	except:
		return default


###############
# Remove unknown values since they have just a new line
###############
def cleanup(wikicode):
	params_list = wikicode.params
	params_to_remove = []

	for param in params_list:
		result = NEW_LINES.match(str(param.value))
		if result:
			params_to_remove.append(param)

	for param in params_to_remove:  # remove after the loop since delete a node changes index
		params_list.remove(param)

	return wikicode


def remove_original(wikicode, diff=""):
	try_or(lambda: wikicode.remove(diff + "HP"), "")
	try_or(lambda: wikicode.remove(diff + "CP"), "")
	try_or(lambda: wikicode.remove(diff + "Defense"), "")
	try_or(lambda: wikicode.remove(diff + "Protection"), "")
	try_or(lambda: wikicode.remove(diff + "MeleeDamage"), "")
	try_or(lambda: wikicode.remove(diff + "RangedDamage"), "")

	try_or(lambda: wikicode.remove(diff + "Crit"), "")
	try_or(lambda: wikicode.remove(diff + "EXP"), "")
	try_or(lambda: wikicode.remove(diff + "GoldMin"), "")
	try_or(lambda: wikicode.remove(diff + "GoldMax"), "")
	try_or(lambda: wikicode.remove(diff + "DropEquip"), "")
	try_or(lambda: wikicode.remove(diff + "DropMisc"), "")

	try_or(lambda: wikicode.remove(diff + "DungeonLocations"), "")
	try_or(lambda: wikicode.remove(diff + "FieldLocations"), "")

	return wikicode


###############
# Tries to move values from wikicode to difficulty_template.
# However, this does not copy CP, so that needs to be done in the caller.
#    This is because Baltane has a different logic
###############
def try_move_values(wikicode, difficulty_template, diff=""):
	difficulty_template.add("HP", try_or(lambda: wikicode.get(diff + "HP").value, "\n"))
	difficulty_template.add("Defense", try_or(lambda: wikicode.get(diff + "Defense").value, "\n"))
	difficulty_template.add("Protection", try_or(lambda: wikicode.get(diff + "Protection").value, "\n"))
	difficulty_template.add("MeleeDamage", try_or(lambda: wikicode.get(diff + "MeleeDamage").value, "\n"))
	difficulty_template.add("RangedDamage", try_or(lambda: wikicode.get(diff + "RangedDamage").value, "\n"))

	difficulty_template.add("Crit", try_or(lambda: wikicode.get(diff + "Crit").value, "\n"))
	difficulty_template.add("EXP", try_or(lambda: wikicode.get(diff + "EXP").value, "\n"))
	difficulty_template.add("GoldMin", try_or(lambda: wikicode.get(diff + "GoldMin").value, "\n"))
	difficulty_template.add("GoldMax", try_or(lambda: wikicode.get(diff + "GoldMax").value, "\n"))
	difficulty_template.add("DropEquip", try_or(lambda: wikicode.get(diff + "DropEquip").value, "\n"))
	difficulty_template.add("DropMisc", try_or(lambda: wikicode.get(diff + "DropMisc").value, "\n"))

	return difficulty_template


def rename_params(params_list):
	for param in params_list:
		if "Mission" in param.name:  # change Mission to MissionsList
			param.name = "MissionsList"
		elif "AllDropMisc" in param.name:
			param.name = "DropMiscCommon"
		elif "AllDropEquip" in param.name:
			param.name = "DropEquipCommon"
	return params_list


###############
# Manually adds data for {{SemanticMonsterDifficultyData template
###############
def make_monster_difficulty(wikicode, monster_type):
	difficulty_template = mwparserfromhell.parse("{{SemanticMonsterDifficultyData\n}}").filter_templates()[0]
	if monster_type == "Normal":
		dungeon = try_or(lambda: wikicode.get("DungeonLocations").value, "").strip()
		field = try_or(lambda: wikicode.get("FieldLocations").value, "").strip()

		difficulty_template.add("Locations", str(dungeon).replace("*None", "") + str(field).replace("*None", "") + "\n")

		difficulty_template.add("Difficulty", "\n")

		# first, move all values to difficulty_template
		difficulty_template = try_move_values(wikicode, difficulty_template)
		difficulty_template.add("CP", try_or(lambda: wikicode.get("CP").value, "\n"))

		# Then remove original values
		wikicode = remove_original(wikicode)

		difficulty_template = cleanup(difficulty_template)
		difficulty_template = str(difficulty_template) + "<nowiki/>\n"
	if monster_type == "Shadow":
		wikicode, difficulty_template = process_params_shadow(wikicode)
	if monster_type == "Lord":
		wikicode, difficulty_template = process_params_lords(wikicode)
	if monster_type == "Baltane":
		wikicode, difficulty_template = process_params_baltane(wikicode)
	if monster_type == "Sidhe":
		wikicode, difficulty_template = process_params_sidhe(wikicode)
	if monster_type == "Bandit":
		wikicode, difficulty_template = process_params_bandit(wikicode)
	return mwparserfromhell.parse(
		re.sub(r'[\n]{2,}', '\n', str(cleanup(wikicode))) + "<nowiki/>\n" + re.sub(r'[\n]{2,}', '\n',
																				   str(difficulty_template)))


###############
# Manually adds data for {{SemanticMonsterDifficultyData template for shadow monsters
###############
def process_params_shadow(wikicode):
	difficulty_total = ""
	params_list = wikicode.params

	params_list = rename_params(params_list)

	for diff in ["Basic", "Intermediate", "Advanced", "Hard", "Elite"]:
		difficulty_template = mwparserfromhell.parse("{{SemanticMonsterDifficultyData\n}}").filter_templates()[0]

		difficulty_template.add("Difficulty", diff + "\n")

		# first, move all values to difficulty_template
		difficulty_template = try_move_values(wikicode, difficulty_template, diff)
		difficulty_template.add("CP", try_or(lambda: wikicode.get(diff + "CP").value, "\n"))

		# Then remove original values
		wikicode = remove_original(wikicode, diff)

		difficulty_template = cleanup(difficulty_template)

		difficulty_total = difficulty_total + str(difficulty_template) + "<nowiki/>\n"
	return wikicode, difficulty_total


###############
# Manually adds data for {{SemanticMonsterDifficultyData template for lords shadow monsters
###############
def process_params_lords(wikicode):
	difficulty_total = ""
	params_list = wikicode.params

	params_list = rename_params(params_list)

	for diff in ["Basic", "Intermediate", "Advanced", "Hard", "Elite"]:
		# Remove unneeded values
		wikicode = remove_original(wikicode, diff)

	diff = "Lord"
	difficulty_template = mwparserfromhell.parse("{{SemanticMonsterDifficultyData\n}}").filter_templates()[0]

	difficulty_template.add("Difficulty", diff + "\n")

	# first, move all values to difficulty_template
	difficulty_template = try_move_values(wikicode, difficulty_template, diff)
	difficulty_template.add("CP", try_or(lambda: wikicode.get(diff + "CP").value, "\n"))

	# Then remove original values
	wikicode = remove_original(wikicode, diff)

	difficulty_template = cleanup(difficulty_template)

	difficulty_total = difficulty_total + str(difficulty_template) + "<nowiki/>\n"
	return wikicode, difficulty_total


###############
# Manually adds data for {{SemanticMonsterDifficultyData template for baltane monsters
###############
def process_params_baltane(wikicode):
	difficulty_total = ""
	params_list = wikicode.params

	params_list = rename_params(params_list)

	for diff in ["Intermediate", "Advanced", "Hard", "Lord"]:
		# Remove unneeded values
		wikicode = remove_original(wikicode, diff)

	for diff in ["Basic", "Elite"]:
		difficulty_template = mwparserfromhell.parse("{{SemanticMonsterDifficultyData\n}}").filter_templates()[0]

		difficulty_template.add("Difficulty", diff + "\n")

		# first, move all values to difficulty_template
		if diff == "Elite":
			if "Giant" in str(wikicode.get("Name").value):
				difficulty_template.add("CP", "-5\n")
			else:
				difficulty_template.add("CP", "-4\n")
		else:
			if "Giant" in str(wikicode.get("Name").value):
				difficulty_template.add("CP", "-4\n")
			else:
				difficulty_template.add("CP", "-3\n")

		difficulty_template = try_move_values(wikicode, difficulty_template, diff)

		# Then remove original values
		wikicode = remove_original(wikicode, diff)

		difficulty_template = cleanup(difficulty_template)

		difficulty_total = difficulty_total + str(difficulty_template) + "<nowiki/>\n"

	return wikicode, difficulty_total


###############
# Manually adds data for {{SemanticMonsterDifficultyData template for sidhe finnachiad monsters
###############
def process_params_sidhe(wikicode):
	difficulty_total = ""
	params_list = wikicode.params

	params_list = rename_params(params_list)
	for param in params_list:
		if "Dungeon" in param.name:  # change Mission to MissionsList
			param.name = "MissionsList"

	for diff in ["Beginner", "Intermediate", "Advanced"]:
		difficulty_template = mwparserfromhell.parse("{{SemanticMonsterDifficultyData\n}}").filter_templates()[0]

		difficulty_template.add("Difficulty", diff + "\n")

		# first, move all values to difficulty_template
		difficulty_template = try_move_values(wikicode, difficulty_template, diff)
		difficulty_template.add("CP", try_or(lambda: wikicode.get(diff + "CP").value, "\n"))

		# Then remove original values
		wikicode = remove_original(wikicode, diff)

		difficulty_template = cleanup(difficulty_template)

		difficulty_total = difficulty_total + str(difficulty_template) + "<nowiki/>\n"

	return wikicode, difficulty_total


###############
# Manually adds data for {{SemanticMonsterDifficultyData template for bandit monsters
###############
def process_params_bandit(wikicode):
	difficulty_total = ""
	params_list = wikicode.params

	params_list = rename_params(params_list)
	for param in params_list:
		if "Location" in param.name:  # change Mission to MissionsList
			param.name = "MissionsList"

	for diff in ["Newbie", "Rookie", "Trained", "Hardened", "Veteran", "Master"]:
		difficulty_template = mwparserfromhell.parse("{{SemanticMonsterDifficultyData\n}}").filter_templates()[0]

		difficulty_template.add("Difficulty", diff + "\n")

		# first, move all values to difficulty_template
		difficulty_template = try_move_values(wikicode, difficulty_template, diff)
		difficulty_template.add("CP", try_or(lambda: wikicode.get(diff + "CP").value, "\n"))

		# Then remove original values
		wikicode = remove_original(wikicode, diff)

		difficulty_template = cleanup(difficulty_template)

		difficulty_total = difficulty_total + str(difficulty_template) + "<nowiki/>\n"
	return wikicode, difficulty_total
