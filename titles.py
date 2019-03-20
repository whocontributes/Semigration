import os
import logging

import page

class MultiBreak(Exception): pass

BASE_DIR = "general_titles"
os.makedirs(BASE_DIR, exist_ok=True)

EFFECT_MAP = {
	"int": "Intelligence",
}

def split_effects(text, effects):
	for effect in html.text.split(","):
		if " " not in effect:
			if effect.strip():
				print(f"Weird effect: '{effect}'")
			else:
				#print("Blank effect")
				pass
			continue
		name, value = effect.rsplit(maxsplit=1)
		effects.append({
			"titleStat": name.strip(),
			"titleStatAmount": value.strip(),
			"titleStatType": effect_type,
		})

titles = page.parse("Titles")
general = titles["General Titles"]

for tp in general.get_templates("TitleTable"):
	name = page.get_text(tp["name"]).strip()
	try:
		effects = []
		try:
			for effect_tag in tp["effects"].filter_tags():
				html = page.Html(effect_tag)
				if html.tag == "span":
					if html.style.color == page.color.red:
						effect_type = "Negative"
					elif html.style.color == page.color.blue:
						effect_type = "Positive"
					else:
						raise MultiBreak(f"Unknown span in effects of '{tp['name']}', skipping")

					text = ", ".join(page.get_text(x) for x in html.contents.filter_text())

					split_effects(text, effects)
					
				elif html.tag != "br":
					raise MultiBreak(f"Unknown html tag in '{tp['name']}', skipping")

			for effect_text in tp["effects"].filter_text():
				text = page.get_text(effect_text).strip()
				if text:
					split_effects(text, effects)
		except MultiBreak as err:
			logging.warning(err.args[0])

		number = page.get_text(tp["#"]).strip()

		with open(os.path.join(BASE_DIR, f"{name}.mediawiki"), "w") as f:
			f.write("\n".join((
				"{{SemanticTitleMainData",
				f"|titleNumber={number}",
				f"|titleName={name}",
				*(
					"|{}={}".format(to_param, page.get_text(tp.get(from_param, "?")).strip())
					for from_param, to_param in [
						("hint", "titleHintDescription"),
						("hintreq", "titleHintRequirement"),
						("desc", "titleDescription"),
						("requirement", "titleRequirement"),
					]
				)
			)))
			f.write("\n}}<nowiki/>\n")

			for effect in effects:
				f.write("\n".join((
					"{{SemanticTitleEffectData",
					*(
						f"|{param}={effect[param]}"
						for param in ["titleStat", "titleStatAmount", "titleStatType"]
					)
				)))
				f.write("\n}}<nowiki/>\n")

			print(f"Wrote file {name}")
	except Exception as err:
		print(f"Got exception for {name}, skipping")
		print(f" Error as: {err}")
