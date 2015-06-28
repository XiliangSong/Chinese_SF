__author__ = 'boliangzhang'


class Node(object):
    def __init__(self, value='', parent=None, index=0, upper_dependency=None):
        self.value = value
        self.children = list()
        self.index = int(index)
        self.upper_dependency = upper_dependency
        self.parent = parent

    def __eq__(self, other):
        return self.index == other.index

    def add_child(self, node):
        self.children.append(node)

    def set_parent(self, node):
        self.parent = node

    def set_value(self, value):
        self.value = value

    def set_upper_dependency(self, d):
        self.upper_dependency = d

    def remove_child(self, node):
        self.children.remove(node)


