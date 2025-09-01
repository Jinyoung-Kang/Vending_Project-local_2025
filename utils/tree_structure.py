class TreeNode:
    def __init__(self, name):
        self.name = name
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def display(self, level=0):
        print("  " * level + f"- {self.name}")
        for child in self.children:
            child.display(level + 1)

def create_drink_tree():
    root = TreeNode("음료")

    coffee = TreeNode("커피")
    coffee.add_child(TreeNode("믹스 커피"))
    coffee.add_child(TreeNode("고급 믹스 커피"))
    coffee.add_child(TreeNode("캔 커피"))
    coffee.add_child(TreeNode("고급 캔 커피"))

    etc = TreeNode("기타")
    etc.add_child(TreeNode("물"))
    etc.add_child(TreeNode("이온음료"))
    etc.add_child(TreeNode("탄산 음료"))
    etc.add_child(TreeNode("특화 음료"))

    root.add_child(coffee)
    root.add_child(etc)

    return root

# 콘솔에서 테스트
if __name__ == "__main__":
    tree = create_drink_tree()
    tree.display()