from anytree import Node
from ParentErrorClass import ParentErrorClass

class ParentMisMatchError(ParentErrorClass):
    def __init__(self, details):
        super().__init__("Parent Mismatch Error", details)

class Parser:
    def __init__(self, tokensArr):
        self.tokens = tokensArr
        self.token_length = len(tokensArr)
        self.comments = []
        self.context_parent = None #this is the parent of the current context
        self.previous_context_parent = None #this is the previous context

        self.holder_stack = [] # (indentation level, parent node) so that we can keep track of the indentation level and traverse back up the tree

        self.tree = None
        self.root = None

    def search_holder_stack_by_indent_level(self, indentation_level: int) -> tuple[int, Node]:
        __buffer = self.holder_stack[::-1] #reverse the holder stack so that we can traverse from the top down

        for holder in __buffer:
            if holder[0] == indentation_level:
                return holder #return the (indent-level, parent-node) (Most recent parent node of the indentation level)
        return None

    def make_tree(self):

        token_index = 0

        for token in self.tokens:

            if token.type == "OPEN":
                #no clue what to do here or why I had open but meh move on
                continue

            elif token.type == "COMMENT":
                self.comments.append(token)
                continue

            elif token.type == "ROOT":
                self.root = Node(token.value)
                self.current_indentation_level = token.indentLevel #initialized to 0 
                self.tree = self.root
                self.context_parent = self.root
                self.holder_stack.append((self.current_indentation_level, self.context_parent))

            elif token.type == "DIR":
                """
                Cases:
                    1) If new directory is on an indentation level greater than the current context parent
                        -> Bump indentation level up by 1
                        -> Add it as a child of the current context parent
                        -> Reset the previous context parent to the current context parent
                        -> Set "new dir node" as the new context parent
                    2) If new directory is on the same indentation level as the current context parent
                        -> Add it as a child of the previous context parent
                        -> Set "new dir node" as the new context parent
                        -> No change to indentation level
                    3) If new directory is on an indentation level less than the current context parent and previous context parent

                        Goal here is to traverse our parent stack based off indentation level until we find the "most recent" 
                        parent node that corresponds to the indentation level of the new directory

                        if our token's indent level is n, then we run a search for token/node of level n-1 (call this search result node -> srn)
                        srn becomes the parent of this token that we are processing 
                        
                        There is a special case where the token's indent level is 0, in which case we just set the root node as the parent

                        now we set the current context parent to the new directory node
                        update indices and add it to our stack
                """
                if token.indentLevel > self.current_indentation_level:
                    if token.indentLevel != self.current_indentation_level + 1:
                        # print("Throw an error for parent indentation level being too far away")
                        return ("ERR", ParentMisMatchError(f"Parent indentation level is {token.indentLevel} and current indentation level is {self.current_indentation_level}"))

                    self.current_indentation_level = token.indentLevel
                    __dirNode = Node(token.value, parent=self.context_parent)
                    self.previous_context_parent = self.context_parent
                    self.context_parent = __dirNode
                    self.holder_stack.append((self.current_indentation_level, self.context_parent))

                elif token.indentLevel == self.current_indentation_level:
                    __dirNode = Node(token.value, parent=self.previous_context_parent)
                    self.context_parent = __dirNode
                    self.holder_stack.append((self.current_indentation_level, self.context_parent))

                elif token.indentLevel < self.current_indentation_level:
                    #special case for when the token's indent level is 1
                    if token.indentLevel == 1:
                        __dirNode = Node(token.value, parent=self.root)
                        self.previous_context_parent = self.root
                        self.context_parent = __dirNode
                        self.current_indentation_level = token.indentLevel
                        self.holder_stack.append((self.current_indentation_level, self.context_parent))
                    else:
                        __most_recent_parent_node = self.search_holder_stack_by_indent_level(token.indentLevel-1)

                        if __most_recent_parent_node == None:
                            # print("Throw an error for parent indentation level not found")
                            return ("ERR", ParentMisMatchError(f"Parent indentation level not found: \nParent indentation level is {token.indentLevel} and current indentation level is {self.current_indentation_level}"))
                        else:
                            __dirNode = Node(token.value, parent=__most_recent_parent_node[1])

                            self.previous_context_parent = __most_recent_parent_node[1]
                            self.context_parent = __dirNode

                            self.current_indentation_level = token.indentLevel
                            self.holder_stack.append((self.current_indentation_level, self.context_parent))

            elif token.type == "FILE":
                """
                Cases:
                    1) New file is on an indentation level greater than the current context parent 
                        -> Add it as a child of the current context parent
                        -> Bump indentation level up by 1
                    2) New file is on the same indentation level as the current context parent
                        -> Add it as a child of the previous context parent
                        -> No change to indentation level
                    3) New file is on an indentation level less than the current context parent
                        -> Traverse back up the tree until we find the parent node corresponding to the indentation level of the new file
                        -> We do this by popping off the holder stack until we find the parent node corresponding to the indentation level of the new file
                        -> reset indentation level to the new file's indentation level
                """
                if token.indentLevel > self.current_indentation_level:
                    self.current_indentation_level = token.indentLevel
                    __fileNode = Node(token.value, parent=self.context_parent)

                elif token.indentLevel == self.current_indentation_level:
                    __fileNode = Node(token.value, parent=self.context_parent)

                elif token.indentLevel < self.current_indentation_level:

                    if token.indentLevel == 1:
                        __fileNode = Node(token.value, parent=self.root)
                        self.context_parent = self.root
                        self.previous_context_parent = None
                        self.current_indentation_level = token.indentLevel
                    else:
                        __PN = self.search_holder_stack_by_indent_level(token.indentLevel - 1)
                        __PCPN = self.search_holder_stack_by_indent_level(token.indentLevel - 2) 

                        if __PN == None:
                            ParentMisMatchError(f"Parent indentation level not found: \nParent indentation level is {token.indentLevel} and current indentation level is {self.current_indentation_level}")
                        else:
                            __fileNode = Node(token.value, parent=__PN[1])
                            self.context_parent = __PN[1]
                            self.previous_context_parent = __PCPN[1] #"should not" be none (keywords SHOULD NOT)
                            self.current_indentation_level = token.indentLevel

                    if __PN == None:
                        # print("Throw an error for parent indentation level not found")
                        return ("ERR", ParentMisMatchError(f"Parent indentation level not found: \nParent indentation level is {token.indentLevel} and current indentation level is {self.current_indentation_level}")) 
                    
                    elif __PN[0] == 0:
                        __fileNode = Node(token.value, parent=self.root)
                        self.previous_context_parent = self.root
                        self.context_parent = __fileNode
                        self.current_indentation_level = token.indentLevel

            elif token.type == "EXIT":
                return  ("", self.tree)

            token_index += 1