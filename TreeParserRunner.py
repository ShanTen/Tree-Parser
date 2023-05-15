from lexer import Lexer
from tree_parser import Parser as TreeParser
from ParentErrorClass import ParentErrorClass
from anytree.exporter import JsonExporter, DotExporter
from anytree import RenderTree

##############################################################################################################################
####################################### Methods On Resultant Tree ############################################################
##############################################################################################################################

def print_tree(tree):
        rStr = ""
        if tree is None:
            return "No tree yet"

        for pre, fill, node in RenderTree(tree):
            rStr += f"{pre}{node.name}\n"
        print(rStr)

def tree_to_svg(tree, filename):
    DotExporter(tree).to_picture(filename)

def tree_to_json_string(tree):
    exporter = JsonExporter(indent=1, sort_keys=False)
    return exporter.export(tree)


##############################################################################################################################
#################################################### Run Methods #############################################################
##############################################################################################################################

class FileNotSpecifiedError(ParentErrorClass):
    def __init__(self):
        self.errorType = "File Not Specified"
        self.details = "No file was specified as an argument"

def run_parser(tree_text):
    lxr = Lexer(tree_text)
    lexer_response_tuple = lxr.tokenize()

    if lexer_response_tuple[0] == "ERR":
        return "ERR",lexer_response_tuple[1]
    else:
        tks = lexer_response_tuple[1]
        parser_response_tuple = TreeParser(tks).make_tree()
        
        if parser_response_tuple[0] == "ERR":
            print(parser_response_tuple[1].stringify())
            return None
        else:
            tree = parser_response_tuple[1]
            return tree

def load_file(filename):
    with open(filename, "r") as f:
        file_content = f.read()
    return run_parser(file_content)
