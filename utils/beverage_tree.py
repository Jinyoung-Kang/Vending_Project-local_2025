class BeverageNode:
    def __init__(self, name, price):
        self.name = name
        self.price = price
        self.left = None
        self.right = None

class BeverageTree:
    def __init__(self):
        self.root = None

    def insert(self, name, price):
        def _insert(node, name, price):
            if not node:
                return BeverageNode(name, price)
            if name < node.name:
                node.left = _insert(node.left, name, price)
            else:
                node.right = _insert(node.right, name, price)
            return node
        self.root = _insert(self.root, name, price)

    def search(self, name):
        def _search(node, name):
            if not node:
                return None
            if node.name == name:
                return node
            elif name < node.name:
                return _search(node.left, name)
            else:
                return _search(node.right, name)
        return _search(self.root, name)