# Parse et importe le RG dans un repository git

# arguments:
#   1. directory containing the RG versions
#   2. output directory. Should be empty or non-existing

import shutil
import sys
import os
import rg_parse
from dulwich.repo import Repo
from os.path import join, exists, isfile
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
    paths_added = []
    paths_removed = []

    for item in commit[1]:
        parent_path = item["path"].strip()
        if not exists(join(output, parent_path)):
            os.makedirs(join(output, parent_path))
        if item["leaf"]:
            fullpath = join(parent_path, "%s.md" % item["titre"])
            with open(join(output, fullpath), "w") as file:
                write_item_file(item, file)
            paths_added.append(fullpath)
        else:
            fullpath = join(parent_path, "README.md")
            with open(join(output, fullpath), "w") as file:
                write_item_file(item, file)
            paths_added.append(fullpath)

    existing = list_files(output, "")
    paths_removed = [path for path in existing if path not in paths_added]
    for p in paths_removed:
        os.remove(join(output,p))
    return paths_added, paths_removed

def list_files(source, accumulator):
    found = [join(accumulator, f) for f in os.listdir(source) if isfile(join(source, f))]
    for d in [f for f in os.listdir(source) if not isfile(join(source, f)) and not f.startswith(".")]:
        found.extend(list_files(join(source, d), join(accumulator, d)))
    return found


if __name__ == "__main__":

    if len(sys.argv) < 3:
        raise ValueError("Usage: python import-rg.py <source> <target>")

    # items = rg_parse.parse(sys.argv[1])
    # dates = sorted(set(map(lambda item: item["date_vigueur"], items)))
    #
    # commits = [(date, [item for item in items if item["date_vigueur"] == date]) for date in dates]

    items = rg_parse.parse(sys.argv[1])
    dates = sorted(set(map(lambda item: item[0], items)))
    commits = [(date, [item[1] for item in items if item[0] == date]) for date in dates]

    repo_loc = sys.argv[2]
    if exists(repo_loc):
        print("Deleting existing output directory: %s" % repo_loc)
        shutil.rmtree(repo_loc)

    os.mkdir(repo_loc)
    repo = Repo.init(repo_loc)

    print("Importing %d commits" % len(commits))

    for i, commit in enumerate(commits[0:5]):
        date = commit[0]
        print("Commit %d dated %s, %d items" % (i, str(date), len(commit[1])))
        paths_added, paths_removed = create_tree(commit, repo_loc)
        repo.stage([path.encode(sys.getfilesystemencoding()) for path in set(paths_added)])

        print("  Removing %d files" % len(paths_removed))
        index = repo.open_index()
        for p in paths_removed:
            print("  Removed: %s" % p)
            del index[p.encode(sys.getfilesystemencoding())]
        index.write()

        repo.do_commit(
            bytes("Règlement général en version du: %s" % date.strftime(FMT), "UTF-8"),
            committer=bytes("Règlement général <rg@amf-france.org>", "UTF-8"),
            commit_timestamp=date.timestamp(),
            commit_timezone=int(TZ_PARIS.localize(date).strftime("%z")) * 36)
