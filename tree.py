
from items import Recipe

class Node:
    def __init__(self, recipe: Recipe):
        self.key = recipe.get_recipe_name()
        self.data = recipe
        self.parent = None
        self.children = dict()

    def set_parent(self, parent):
        self.parent = parent

    def add_child(self, child):
        self.children[child.get_name()] = child
        child.set_parent(self)

    def get_name(self) -> str:
        return self.key

    def remove_child(self, recipe_name: str):

        if self.children.__contains__(recipe_name):
            node = self.children[recipe_name]
            self.children.pop(recipe_name)
            node.set_parent(None)
        else:
            print(recipe_name)
            for i in self.children.keys():
                print(i)


    def get_parent(self):
        return self.parent


    def get_children(self):
        return self.children

    def get_recipe_requirements(self) -> [str]:
        return self.data.get_requirement_names()

    def get_recipe(self):
        return self.data



def tree_search(key: str, base: Node):
    next_nodes = []
    current_nodes = base.get_children().values()

    if base.get_name() == key:
        return base

    while not current_nodes == []:
        for node in current_nodes:
            if node.get_name() == key:
                return node
            else:
                next_nodes.extend(node.get_children().values())

        current_nodes = next_nodes
        next_nodes = []
    return None

def print_tree(base: Node):
    next_children = []
    current_nodes = [base]

    message = "\n ```"

    while not current_nodes == []:
        for i in current_nodes:
            next_children.extend(i.get_children().values())

            parent = i.get_parent()
            if parent is None:
                p_info = "No parent"
            else:
                p_info = parent.get_name()

            message = message + p_info+":["+ i.get_name()+"] "
        message = message + "\n"
        current_nodes = next_children
        next_children = []
    return message + "```"






