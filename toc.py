## toc.py

import os
from os.path import basename, join, isfile, exists
import re

class Node:
    def __init__(self, name, children = [], path = ""):
        self.name = name
        self.children = sorted(children, key=lambda c: c.name.replace(".md", ""))
        self.path = path

    def leaf(self):
        return len(self.children) == 0

    def child(self, n):
        filter = [c for c in self.children if c.name == n]
        if len(filter) == 0:
            return None
        else:
            return filter[0]

    def __str__(self):
        if self.leaf():
            return "{at %s: leaf name: %s}" % (self.path, self.name)
        else:
            return "{at %s: branch name: %s, children: [\n%s\n]}" % (self.path, self.name, ",\n".join(str(c) for c in self.children))


def create_toc(base, recursion = 1):
    '''
    Create the table of contents by exploring the file system
    Arguments:
    - base: the base directory to start the exploration on
    - recursion: if None, then create a ToC without depth limit.
                 if 1, then create a 1-level ToC that points to unlimited-level sub-ToCs
                 Optionally in the future we may support > 1 recursion
    '''
    root = explore(base, "")

    write_toc(base, root, recursion)
    if recursion is not None:
        for level in root.children:
            write_toc(join(base, level.name), level, None)


def write_toc(folder, tree, recursion):
    toc = "".join([serialize_from(c, join(folder, c.name), 0, "", recursion) for c in tree.children])
    readme = join(folder, "README.md")
    with open(readme, "a") as file:
        file.write("\n")
        file.write(toc)

def explore(source, path):
    if isfile(source):
        return Node(basename(source), path=path)
    else:
        return Node(basename(source), [explore(join(source,c), join(path,c)) for c in os.listdir(source) if not basename(c) == "README.md"], path=path)

def serialize_from(node, folder, indent, accumulator, recursion=None, labels=None):
    rec = recursion - 1 if recursion is not None else None
    if node.leaf():
        return ("  " * indent) + "1. [" + node.name.replace(".md", "") + "](" + accumulator + node.name + ")\n"
    else:
        if labels is not None:
            title = labels[accumulator + node.name]
        elif exists(join(folder, "README.md")):
            readme = join(folder, "README.md")
            with open(readme, "r") as r:
                title = r.readline().strip()
        else:
            title = node.name
        result = ("  " * indent) + "1. [" + title + "](" + accumulator + node.name + ")\n"
        if rec is not 0:
            for n in node.children:
                c = join(folder, n.name)
                if exists(c):
                    result = result + serialize_from(n, c, indent + 1, accumulator + node.name + "/", rec, labels)
                else:
                    print("Ooops, child %s not found in path %s" % (n.name, folder))

        return result

def compute_toc(folder, items):
    print("Folder is %s" % basename(folder))
    root = explore(folder, "")
    labels = dict(zip([re.sub(r'^%s/(.+)/$' % basename(folder), r'\1',i["path"].strip()) for i in items if not i["leaf"]], [i["titre"].strip() for i in items if not i["leaf"]]))

    return "".join([serialize_from(c, join(folder, c.name), 0, "", labels=labels) for c in root.children])

if __name__=="__main__":
    n = Node("hello", [Node("world"), Node("here")])
    print(n)
    print(n.child("world"))
