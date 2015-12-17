class Node:
    def __init__(self, name, title, path):
        self.name = name
        self.title = title
        self.children = []
        self.parent = None
        self.path = path

    def push(self, node):
        node.parent = self
        self.children.append(node)

    def pop(self):
        return self.parent

    def leaf(self):
        return len(self.children) == 0

    def root(self):
        return self.parent == None

def serialize(node, indent):
    if node.leaf():
        return ("  " * indent) + "1. [" + node.title + "](" + node.path + "/" + node.name + ".md)"
    else:
        this = ("  " * indent) + "1. [" + node.title + "](" + node.path + ")"
        return "\n".join([this] + [serialize(c, indent + 1) for c in node.children])

def compute_toc(items):
    root = Node("", "", "")
    node = root
    for item in items:
        if not item["leaf"]:
            # either nest or pop
            if item["path"].count('/') <= node.path.count('/'):
                while not item["path"].count('/') > node.path.count('/') and not node.root():
                    node = node.pop()
            if node.root(): print("At root")
            n = Node(item["name"] , item["titre"], item["path"])
            node.push(n)
            node = n
        else:
            node.push(Node(item["name"], item["titre"], item["path"]))
    return "\n".join([serialize(c, 0) for c in root.children])
