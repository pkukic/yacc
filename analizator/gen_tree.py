class GenTree:
    
    _root_node = None
    valid = None


    def __init__(self, root_node):
        if root_node == None:
            self.valid = False
        else:
            self._root_node = root_node
            self.valid = True


    def print(self):
        if self.valid:
            self._root_node.print(0)
