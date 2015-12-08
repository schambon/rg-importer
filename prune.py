import os
from os.path import join, isfile, basename, exists

def prune(node):
    this = len([ f for f in os.listdir(node) if isfile(join(node, f)) and f != "README.md"]) == 0

    print("  Examine for pruning: %s, local=%r" % (node, this))

    if all([prune(join(node,d)) for d in os.listdir(node) if
            not isfile(join(node, d)) and d != ".git"]) and this:
        print("    Pruning tree: %s" % node)
        readme = join(node, "README.md")
        if exists(readme):
            os.remove(readme)
        # it may be that node has already been deleted by nested removedirs
        if exists(node): os.removedirs(node)
        return True
    else:
        print("    Not pruning tree: %s" % node)
        return False
