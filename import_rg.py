# Parse et importe le RG dans un repository git

# arguments:
#   1. directory containing the RG versions
#   2. output directory. Should be empty or non-existing

import shutil
import sys
import os

import time

from dulwich.repo import Repo
from dulwich.objectspec import parse_object
from dulwich.objects import Commit, Tag
from os.path import join, exists, isfile, basename
from pytz import timezone

import rg_parse, content_cleaner as cc, toc, toc2
from prune import prune


TZ_PARIS = timezone("Europe/Paris")
FMT = "%d/%m/%Y"
ISO_8601 = "%Y-%m-%d"

def write_item_file(item, file):
    file.write(item["titre"])
    file.write("\n")
    file.write(len(item["titre"]) * "=")
    file.write(cc.clean(item["content"]))
    file.write("\n")


def create_tree(commit, output, readme=True, main={}):
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
            fullpath = join(parent_path, "%s.md" % item["name"])
            with open(join(output, fullpath), "w") as file:
                write_item_file(item, file)
            paths_added.append(fullpath)
        elif readme:
            fullpath = join(parent_path, "README.md")
            with open(join(output, fullpath), "w") as file:
                write_item_file(item, file)
            paths_added.append(fullpath)

    existing = list_files(output, "")

#    base = join(output, os.listdir(output)[0])
    base = output
    print("Base is: %s" % base)
    ## Whatever happens, there'll be a README at the root
    # paths_added.append(join(basename(base), "README.md"))
    paths_added.append("README.md")

    paths_removed = [path for path in existing if path not in paths_added]
    for p in paths_removed:
        os.remove(join(output,p))
    prune(output)

    if readme:
        toc.create_toc(base)
    else:
        print("Writing TOC")
        # toc_md = toc.compute_toc(base, commit[1])
        toc_md = toc2.compute_toc(commit[1])
        with open(join(base, "README.md"), "w") as file:
            if "name" in main:
                file.write("%s\n" % main["name"])
                file.write("=" * len(main["name"]))
                file.write("\n\n")
                file.write(main["title"] + "\n")
                file.write("\n\n".join(main["content"].split("\n")))
            else:
                file.write("%s\n" % basename(base))
                file.write("=" * len(basename(base)))
            file.write("\n\n")
            file.write(toc_md)
    return paths_added, paths_removed

def list_files(source, accumulator):
    found = [join(accumulator, f) for f in os.listdir(source) if isfile(join(source, f))]
    for d in [f for f in os.listdir(source) if not isfile(join(source, f)) and not f.startswith(".")]:
        found.extend(list_files(join(source, d), join(accumulator, d)))
    return found

def do_import(commits, repo_loc, overwrite = True, author="Règlement général <rg@amf-france.org>"):
    if exists(repo_loc):
        if overwrite:
            print("Deleting existing output directory: %s" % repo_loc)
            shutil.rmtree(repo_loc)

            os.mkdir(repo_loc)
            repo = Repo.init(repo_loc)
        else:
            repo = Repo(repo_loc)
    else:
        os.mkdir(repo_loc)
        repo = Repo.init(repo_loc)


    print("Importing %d commit(s)" % len(commits))

    for i, commit in enumerate(commits):
        date = commit[0]
        print("Commit %d dated %s, %d items" % (i, str(date), len(commit[1])))
        paths_added, paths_removed = create_tree(commit, repo_loc, readme=False, main=commit[2] if len(commit) == 3 else {})
        repo.stage([path.encode(sys.getfilesystemencoding()) for path in set(paths_added)])

        index = repo.open_index()

        print("  Removing %d files" % len(paths_removed))
        for p in paths_removed:
            print("  Removed: %s" % p)
            del index[p.encode(sys.getfilesystemencoding())]
        index.write()

        author = bytes(author, "UTF-8")

        repo.do_commit(
            bytes("Version du %s" % date.strftime(FMT), "UTF-8"),
            committer=author,
            commit_timestamp=date.timestamp(),
            commit_timezone=int(TZ_PARIS.localize(date).strftime("%z")) * 36)

        ## create tag
        tag_name = bytes(date.strftime(ISO_8601), "UTF-8")
        object = parse_object(repo, "HEAD")
        tag = Tag()
        tag.tagger = author
        tag.name = tag_name
        tag.message = b''
        tag.object = (type(object), object.id)
        tag.tag_time = int(time.time())
        tag.tag_timezone = int(TZ_PARIS.localize(date).strftime("%z")) * 36
        repo.object_store.add_object(tag)
        tag_id = tag.id

        repo.refs[b'refs/tags/' + tag_name] = tag_id

    repo.close()



if __name__ == "__main__":

    if len(sys.argv) < 3:
        raise ValueError("Usage: python import-rg.py <source> <target>")

    items = rg_parse.parse(sys.argv[1])
    dates = sorted(set(map(lambda item: item[0], items)))
    commits = [(date, [item[1] for item in items if item[0] == date]) for date in dates]

    repo_loc = sys.argv[2]
