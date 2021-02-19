# whocontributes 07/04/2019
import difflib
import getpass
import re
import webbrowser
import clipboard
import mwclient
import mwparserfromhell
import Bot

from Monster_Params_Parser import make_monster_difficulty, try_or

import semigration
from semigration.section import URL_WIKI_BASE, URL_WIKI_PATH
from semigration.upload import URL_EDIT

warning_text = ""  # any text that needs to be sent to the user for review. For example, "old exp was 165-225. please double check this."

AUTO_UPLOAD = False
BOT_OBJ = None


# strip anything before template
# also append nowiki after template
def prepare_wikicode(current_page):
    text = current_page.text()
    split = text.split("{{SemanticMonsterData")
    res = "{{SemanticMonsterData" + split[1]

    res = res.replace("}}", "}}<nowiki/>")
    return res


def process_page(page):
    made_changes = False
    try:
        current_page = semigration.parse(page)
    except:
        print("Failed to find page '%s'" % page)
        return False

    if "SemanticMonsterData" in str(current_page.templates):  # wa want SemanticMonsterData.MissionsList
        for item in current_page.templates:

            if "SemanticMonsterData" in str(item):
                original = str(item['MissionsList'])
                new_missions = original.replace("*", ",")
                new_missions = new_missions.replace("\n", "")

                # keep last newline
                new_missions = new_missions + "\n"
                new_missions = new_missions.lstrip(',')
                if original != new_missions:
                    item['MissionsList'].replace(original, new_missions)
                    print("[PAGE %s]  %s has been changed to\n%s" % (page, original, new_missions))
                    made_changes = True
                else:
                    print("[PAGE %s]  no change. Do not fix this page" % (page))

    if AUTO_UPLOAD and made_changes:
        BOT_OBJ.edit_and_save(page, prepare_wikicode(current_page),
                              "Updated mission list to csv. Please check my work!")

    return made_changes


def ask_auto_upload():
    global AUTO_UPLOAD, BOT_OBJ

    value = input("Do you want to auto upload? (y/n) ")
    if value.lower() == "y":
        AUTO_UPLOAD = True
        USERNAME = input("What is your mabi wiki username? ")
        PASSWORD = getpass.getpass("What is your mabi wiki password? ")
        BOT_OBJ = Bot.Bot(USERNAME, PASSWORD)


def main():
    ask_auto_upload()
    with open("PagesToProcess.txt", "r") as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if AUTO_UPLOAD and process_page(line.rstrip('\n')):
            print("Finished page::{0}. ({1}/{2})\n===".format(line.rstrip('\n'), i, len(lines)))
            #input("Waiting for user")


if __name__ == "__main__":
    import os

    if not os.path.isdir("output"):
        os.mkdir("output")  # Save files to upload later
    main()
