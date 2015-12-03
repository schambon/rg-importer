## toc.py

import os
from os.path import basename, join, isfile, exists

class Node:
    def __init__(self, name, children = []):
        self.name = name
        self.children = sorted(children, key=lambda c: c.name.replace(".md", ""))

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
            return "{leaf name: %s}" % self.name
        else:
            return "{branch name: %s, children: [\n%s\n]}" % (self.name, ",\n".join(str(c) for c in self.children))


def create_toc(base):
    root = explore(base)
    # print("---\nFound tree:\n---\n%s" % str(root))

    toc = "".join([serialize_from(c, join(base, c.name), 0, "") for c in root.children])
    readme = join(base, "README.md")
    with open(readme, "a") as file:
        file.write("\n")
        file.write(toc)


def explore(source):
    if isfile(source):
        return Node(basename(source))
    else:
        return Node(basename(source), [explore(join(source,c)) for c in os.listdir(source) if not basename(c) == "README.md"])

def serialize_from(node, folder, indent, accumulator):
    if node.leaf():
        return ("  " * indent) + "1. [" + node.name.replace(".md", "") + "](" + accumulator + node.name + ")\n"
    else:
        readme = join(folder, "README.md")
        with open(readme, "r") as r:
            title = r.readline().strip()
        result = ("  " * indent) + "1. [" + title + "](" + accumulator + node.name + ")\n"
        for n in node.children:
            c = join(folder, n.name)
            if exists(c):
                result = result + serialize_from(n, c, indent + 1, accumulator + node.name + "/")
            else:
                print("Ooops, child %s not found in path %s" % (n.name, folder))

        return result

if __name__=="__main__":
    n = Node("hello", [Node("world"), Node("here")])
    print(n)
    print(n.child("world"))
