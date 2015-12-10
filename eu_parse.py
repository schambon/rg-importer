from bs4 import BeautifulSoup, element
from datetime import datetime
import re

levels = [["document"], ["title", "final provisions", "titre", "dispositions finales"], ["chapter", "chapitre"], ["section"]]


class Section:
    def __init__(self, level, name, parent):
        self.level = level
        self.name = name.strip()
        self.parent = parent
        self.title = None
        self.text = ""
        self.children = []

    def leaf(self):
        return False

    def push(self, section):
        self.children.append(section)

    def pop(self):
        return self.parent

    def __str__(self):
        indent = " " * self.level
        res = ""
        res = "%s%sName:  %s\n" % (res, indent, self.name)
        res = "%s%sLevel: %d\n" % (res, indent, self.level)
        res = "%s%sTitle: %s\n" % (res, indent, self.title)
        for child in self.children:
            res = "%s%s" % (res, str(child))
        return res

class Article(Section):
    def __init__(self, name, parent):
        super().__init__(99, name, parent)

    def __str__(self):
        indent = " " * (self.parent.level + 2)

        text = ("\n   " + indent).join(self.text.split("\n"))

        res = ""
        res = "%s%s%s\n" % (res, indent, self.name)
        res = "%s%s%s\n" % (res, indent, "-" * len(self.name))
        res = "%s%sTitle: %s\n" % (res, indent, self.title)
        res = "%s%sText:" % (res, indent)
        res = res + text + "\n"
        return res

    def leaf(self):
        return True

def level_index(level):
    for i, ls in enumerate(levels):
        for j, lvl in enumerate(ls):
            if level.lower().startswith(lvl):
                return i
    return 99

def parse(text):
    soup = BeautifulSoup(text, "html5lib")
    date = datetime.strptime(
        soup.find("p", class_="hd-date").get_text().strip(), "%d.%m.%Y")

    main_doc = parse_doc([line for line in soup.body.contents if type(line) == element.Tag])

    print("Parsed:\n")
    print(main_doc)

    return (date, [x for title in main_doc.children for x in flatten(title, "")], {"name": main_doc.name, "title": main_doc.title, "content": main_doc.text})


def parse_doc(lines):
    current_section = None
    current_article = None
    for i, line in enumerate(lines):
        text = line.get_text().strip()
        cls = line.attrs["class"][0] if "class" in line.attrs else None
        if cls == "final":
            break
        elif cls == "doc-ti":
            # we have the document start!
            # initialize the current section
            if current_section is None:
                current_section = Section(level=0, name=text, parent=None)
            else:
                current_section.title = current_section.title + " " + text if current_section.title is not None else text

        elif cls == "ti-section-1":
            # we have a section!
            # now:
            #  - if the section is lower than current_section: push a new section
            lvl = level_index(text)
            if lvl > current_section.level:
                section = Section(level=lvl, name=text, parent=current_section)
                current_section.push(section)
                current_section = section
            else:
                # - if the section is higher than current_section: pop until we are at a higher level
                #   then push a new section
                while lvl <= current_section.level:
                    current_section = current_section.pop()
                section = Section(level=lvl, name=text, parent=current_section)
                current_section.push(section)
                current_section = section
            # in any case, close the current article
            current_article = None

        elif cls == "ti-section-2":
            # we have a section title
            current_section.title = text

        elif cls == "ti-art":
            # articles
            current_article = Article(text, parent=current_section)
            current_section.push(current_article)
        elif cls == "sti-art":
            current_article.title = text
        elif current_article is not None:
            current_article.text = current_article.text + "\n\n" + cleanup(text)
        elif current_section is not None:
            current_section.text = current_section.text + "\n" + cleanup(text)

    # Pop back up to the root
    while current_section.level > 0:
        current_section = current_section.pop()

    return current_section


def cleanup(line):
    t = re.sub(r'\n', r'', line)
    t = re.sub(r'(\s)\s*', r'\1', t)
    return t

def title(node):
    return node.name + " - " + node.title if node.title is not None else node.name

def unslash(s):
    return s.replace("/", "-")

def flatten(node, accumulator=""):
    this = {
        "titre": title(node),
        "content": node.text,
        "name": node.name,
        "path": accumulator,
        "leaf": node.leaf()
    }
    if (node.leaf()):
        return [this]
    else:
        path = accumulator + "/" + unslash(node.name) if accumulator != "" else unslash(node.name)
        this["path"] = path
        return [this] + [x  for n in node.children for x in flatten(n, path)]
