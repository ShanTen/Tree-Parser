from TreeParserRunner import *

def run(tree_text):
    response_tuple = run_parser(tree_text)
    if response_tuple != None:
        tree = response_tuple
        print_tree(tree)
        tree_to_image(tree, "file_structure.png")
        #print(tree_to_json_string(tree))

if __name__ == '__main__':
    import sys
    
    tree_file = ""
    if len(sys.argv) > 1:
        tree_file = sys.argv[1]
    else:
        FileNotSpecifiedError().stringify()
    with open(tree_file, "r") as f:
        tree_text = f.read()
    run(tree_text)