# Parse et importe le RG dans un repository git

# arguments:
#   1. directory containing the RG versions
#   2. output directory. Should be empty or non-existing

import shutil
import sys
import os
import rg_parse
from dulwich.repo import Repo
from os.path import join, exists
from pytz import timezone

TZ_PARIS = timezone("Europe/Paris")
FMT = "%d/%m/%Y"

def write_item_file(item, file):
    file.write(item["titre"])
    file.write("\n")
    file.write(len(item["titre"]) * "=")
    file.write("\n\n")
    file.write("Date de modification: %s\n" % item["date_modif"].strftime(FMT))
    file.write("Date d'entrée en vigueur: %s\n\n" % item["date_vigueur"].strftime(FMT))
    file.write(item["content"])
    file.write("\n")


def create_tree(commit, output):
    '''
    Create the tree structure for the commit
    Return the list of full file paths for the commit, from the output dir
    '''
    paths = []
    for item in commit[1]:
        parent_path = item["path"].strip()
        if not exists(join(output, parent_path)):
            os.makedirs(join(output, parent_path))
        if item["leaf"]:
            fullpath = join(parent_path, "%s.md" % item["titre"])
            with open(join(output, fullpath), "w") as file:
                write_item_file(item, file)
            paths.append(fullpath)
        else:
            fullpath = join(parent_path, "README.md")
            with open(join(output, fullpath), "w") as file:
                write_item_file(item, file)
            paths.append(fullpath)
    return paths

if len(sys.argv) < 3:
    raise ValueError("Usage: python import-rg.py <source> <target>")

#items = sorted(rg_parse.parse(sys.argv[1]), key=lambda item: item["date_vigueur"])
items = rg_parse.parse(sys.argv[1])
dates = sorted(set(map(lambda item: item["date_vigueur"], items)))

commits = [(date, [item for item in items if item["date_vigueur"] == date]) for date in dates]

# for i in range(0,1):
#     print(str(commits[i][0]) + " -> " + str(len(commits[i][1])) + " items at that date")
#     for j in range(0,3):
#         print("   Path: %s" % commits[i][1][j]["path"])

repo_loc = sys.argv[2]
if exists(repo_loc):
    print("Deleting existing output directory: %s" % repo_loc)
    shutil.rmtree(repo_loc)

os.mkdir(repo_loc)
repo = Repo.init(repo_loc)

print("Importing %d commits" % len(commits))

for i, commit in enumerate(commits):
    date = commit[0]
    print("Commit %d dated %s, %d items" % (i, str(date), len(commit[1])))
    paths = create_tree(commit, repo_loc)
    # for path in set(paths):
    #     print("     %s" % path)
    repo.stage([path.encode(sys.getfilesystemencoding()) for path in set(paths)])

    repo.do_commit(
        bytes("RG entré en vigueur le %s" % date.strftime(FMT), "UTF-8"),
        committer=bytes("Règlement général <rg@amf-france.org>", "UTF-8"),
        commit_timestamp=date.timestamp(),
        commit_timezone=int(TZ_PARIS.localize(date).strftime("%z")) * 36)
