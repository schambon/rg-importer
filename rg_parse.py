## rg_parse.py

import xml.etree.ElementTree as ET
import datetime
import os
from os.path import isfile, join, basename
import re
import sys
import unicodedata

def parse(source):
    files = [join(source,f) for f in os.listdir(source) if isfile(join(source, f)) and f.endswith(".xml")]
    return [item for f in files for item in parse_file(f)]


def parse_file(file):
    print("Parsing file: %s" % file)
    tree = ET.parse(file)
    items = parse_item(tree.getroot().find("item"), "")
    # export(items, file)
    return items

def parse_item(item, path):
    titre = item.find("versions/version/titre")
    if titre is None:
        raise ValueError("Titre non trouvé")
    s_titre = titre.text.strip()
    content = item.find("versions/version/content")
    s_content = content.text.strip() if content is not None else ""
    date_vigueur = datetime.datetime.strptime(item.find('versions/version/dateVigueur').text.strip(), '%Y-%m-%d')
    date_modif = datetime.datetime.strptime(item.find('versions/version/dateModification').text.strip(), '%Y-%m-%d')

    this = {"titre": s_titre, "content": s_content, "date_vigueur": date_vigueur, "date_modif": date_modif}

    # est-ce une feuille de l'arbre ?
    this["leaf"] = True if len(item.findall("items/item")) is 0 else False

    if this["leaf"]:
        # si c'est une feuille, on n'enregistre que le chemin parent
        this["path"] = path
        return [this]
    else:
        current_path = join(path, as_folder(s_titre))
        this["path"] = current_path + "/"
        return [this] + [f for it in item.findall("items/item") for f in parse_item(it, current_path)]

def as_folder(titre):
    return titre[0:titre.find(' -')] if ' -' in titre else titre

def export(items, file):
    leaves = sorted(set([join(item["path"], item["titre"]) for item in items if item["leaf"]]))
    with open("./index-%s.txt" % basename(file), "w") as out:
        for leaf in leaves:
            out.write(leaf)
            out.write("\n")

if __name__ == "__main__":
    items = parse(sys.argv[1])
    print(items[0:3])
