import os
import re
import glob
import logging
import argparse

import page

class MultiBreak(Exception): pass

EFFECT_MAP = {
	"int": "Intelligence",
}


SPLITTER = re.compile(r'(?<=[\d%]),')


def split_effects(text, effects, effect_type):
	for effect in SPLITTER.split(text):
		if " " not in effect:
			effect = effect.strip()
			if effect and effect != ",":
				print(f"  Weird effect: '{effect}'")
			continue
		name, value = effect.rsplit(maxsplit=1)
		effects.append({
			"titleStat": name.strip(),
			"titleStatAmount": value.strip(),
			"titleStatType": effect_type,
		})


def download(filename):
	titles = page.parse("Titles")
	with open(filename, "w", encoding="utf8") as f:
		f.write(titles.text())
	return titles


def load(filename):
	with open(filename, encoding="utf8") as f:
		return page.parse(text=f.read())["Titles"]


def process(titles, folder):
	os.makedirs(folder, exist_ok=True)

	general = titles["General Titles"]

	for tp_idx, tp in enumerate(general.get_templates("TitleTable")):
		name = page.get_text(tp["name"]).strip()
		print(f"Processing: {name}")
		try:
			effects = []
			notes = ""
			try:
				effects_text = page.get_text(tp["effects"]).strip()
			except KeyError:
				effects_text = "?"

			if effects_text.startswith("None, but see"):
				# Transformation title
				try:
					notes = str(tp["effects"].contents)
				except AttributeError:
					notes = str(tp["effects"])
			elif effects_text == "?":
				print("  Unknown effects")
			else:
				try:
					for effect_tag in tp["effects"].filter_tags(recursive=False):
						html = page.Html(effect_tag)
						if html.tag == "span":
							if html.style.color == page.color.red:
								effect_type = "Negative"
							elif html.style.color == page.color.blue:
								effect_type = "Positive"
							else:
								raise MultiBreak("  Unknown span in effects, skipping")

							text = ", ".join(page.get_text(x) for x in html.contents.filter_text(recursive=False))

							split_effects(text, effects, effect_type)

						elif html.tag == "i":
							notes = html.text.lstrip("(").rstrip(")")
							
						elif html.tag != "br":
							raise MultiBreak(f"  Unknown html tag '{html.tag}', skipping")

					for effect_text in tp["effects"].filter_text(recursive=False):
						text = page.get_text(effect_text).strip()
						if text:
							split_effects(text, effects, effect_type)
				except MultiBreak as err:
					logging.warning(err.args[0])

			number = page.get_text(tp["#"]).strip()
			try:
				if int(number) > 100:
					number= "*"
			except ValueError:
				pass

			# TODO: hint [html] comments

			filename = f"{tp_idx:03d}-{name}.mediawiki"
			cleaned_filename = page.clean_filename(filename)
			if filename != cleaned_filename:
				cleaned_filename = page.clean_filename(f"{tp_idx:03d}-{name}.badname.mediawiki")

			with open(os.path.join(folder, cleaned_filename), "w", encoding="utf8") as f:
				f.write("\n".join((
					"{{SemanticTitleMainData",
					f"|titleNumber={number}",
					f"|titleName={name}",
					*(
						"|{}={}".format(to_param, page.get_text(tp.get(from_param, "(unknown)")).strip())
						for from_param, to_param in [
							("hint", "titleHintDescription"),
							("hintreq", "titleHintRequirement"),
							("desc", "titleDescription"),
							("requirement", "titleRequirement"),
						]
					)
				)))
				if notes:
					f.write(f"\n|titleNotes={notes}")
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

				print(f"  Wrote file")
		except Exception as err:
			logging.error(f"  Got exception, skipping")
			logging.exception(err)


def upload(folder):
	text = {
		"badname": "Unable to use given page name, please enter a new one.\n  Invalid name: {name}",
		"suggest": 'Enter a new name or leave blank to use "{name}"',
		"enter": "Enter the title (or a 2 or 3 for gendered titles)",
		"enter1/1": "Enter title:",
		"enter1/3": "Enter neuter title:",
		"enter2/3": "Enter male title:",
		"enter3/3": "Enter female title:",
		"enter1/2": "Enter male title:",
		"enter2/2": "Enter female title:",
	}
	for file in glob.glob(os.path.join(folder, "**.mediawiki")):
		name = os.path.basename(file)[4:-10]
		with open(file) as f:
			contents = f.read()
		if name.endswith(".badname"):
			page.upload(name, contents, text, bad=True)
		else:
			page.upload(name, contents, text)


parser = argparse.ArgumentParser(description="Migrated general titles")
parser.add_argument("-d", "--download", action="store_true",
	help="Download the titles page, process it, and write it out.")
parser.add_argument("-D", "--download-to", action="store_true",
	help="Download the titles page to a file. (Default: titles.mediawiki)")
parser.add_argument("-p", "--process", action="store_true",
	help="Process a downloaded page. (Default: titles.mediawiki)")
parser.add_argument("-u", "--upload", action="store_true",
	help="Upload the already downloaded titles to semantic spaces.")
parser.add_argument("-f", "--folder", default="general_titles",
	help="Specify the folder to dump titles into. (Default: general_titles)")
parser.add_argument("file", nargs="?", default="titles.mediawiki",
	help=argparse.SUPPRESS)

args = parser.parse_args()

if args.download or args.download_to:
	titles = download(args.file)
	if args.download:
		process(titles, args.folder)
elif args.process:
	titles = load(args.file)
	process(titles, args.folder)

if args.upload:
	upload(args.folder)
