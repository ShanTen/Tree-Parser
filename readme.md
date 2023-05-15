# Serialized Tree Parser

*TLDR;* Converts mark up in the form of a an ascii tree into an iterable.

## Objective
- I have some data in a text file, it looks like a tree. 
- I wanted to convert this data into a tree structure in memory and iterate it.
- Maybe even re-create original file/folder structure as an empty file

### Objective In Detail
Assuming I have a file like this (serialized data)

```
...
[Heading] 
+--- geography
|   +--- public/ 
|   +--- countries
|   +--- seas
|   |   +--- indian_ocean
|   |   +--- pacific_ocean
|   |   \--- atlantic_ocean
+--- history
|   +--- Ancient history
|   +--- Medieval history
|   +--- Modern history
|   |   +--- WW1
|   |   \--- WW2
\--- Physics
```

I wanted to make this into an object which I can iterate later (hierarchial data).  
Maybe even something like a json object or an image of a directed graph.

Something like this:  
![Tree as Graph](https://github.com/ShanTen/Tree-Parser/blob/master/img_out/tree.png)

## Design
+ Uses a lexer to tokenize the input and then a parser to analyze "context" of each token and create a tree 
+ Refer [Lexer.py](https://github.com/ShanTen/Tree-Parser/blob/master/lexer.py) and [tree_parser.py](https://github.com/ShanTen/Tree-Parser/blob/master/lexer.py) for more details
+ Uses [AnyTree](https://pypi.org/project/anytree/) for the tree iterable which is honestly better than anything I could make.

## Issues in Project
+ Better error handling
+ Ironing out bugs 
+ Built originally to replicate file trees and not as a general purpose mark up language
+ Cannot replicate files (yet)
+ There is no tool to generate the serialized data (yet)

## Usage

### Using run.py
```python
from TreeParserRunner import *

def run(tree_text):
    response_tuple = run_parser(tree_text)
    if response_tuple != None:
        tree = response_tuple 
        print_tree(tree) #In this case, tree is the parsed tree in the form of a tree :P
        tree_to_image(tree, "img_out/file_structure.png")
        print(tree_to_json_string(tree))

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
```

### Tree File (project.tree)
```
<TreeStart> 
#File Structure for messaging app
[messaging-app] 
+--- client/  
|   +--- public/ 
|   |   \--- index.html  #The place where my index.html is
|   +--- src/ 
|   |   +--- components/ 
|   |   |   \--- App.vue 
|   |   +--- views/ 
|   |   |   \--- Chat.vue #This is a comment
|   |   +--- main.js
|   |   \--- router.js
|   +--- package.json
|   +--- babel.config.js
|   \--- webpack.config.js
+--- server/
|   +--- index.js
|   +--- controllers/
|   |   \--- chat.js
|   +--- models/
|   |   \--- User.js
|   +--- routes/
|   |   \--- chat.js
|   \--- package.json #make sure to npm install in this folder
+--- .gitignore
\--- README.md
<TreeEnd>
```

Running the method
```
~$ python run.py trees/project.tree
```

### Output
```json
messaging-app
├── client
│   ├── public
│   │   └── index.html
│   ├── src
│   │   ├── components
│   │   │   └── App.vue
│   │   ├── views
│   │   │   └── Chat.vue
│   │   ├── main.js
│   │   └── router.js
│   ├── package.json
│   ├── babel.config.js
│   └── webpack.config.js
├── server
│   ├── index.js
│   ├── models
│   │   └── User.js
│   ├── routes
│   │   └── chat.js
│   └── package.json
├── controllers
│   └── chat.js
├── .gitignore
└──  README.md

{
 "name": "messaging-app",
 "children": [
  {
   "name": "client",
   "children": [
    {
     "name": "public",
     "children": [
      {
       "name": "index.html"
      }
     ]
    },
    {
     "name": "src",
     "children": [
      {
       "name": "components",
       "children": [
        {
         "name": "App.vue"
        }
       ]
      },
...
```
Full json output [here](https://github.com/ShanTen/Tree-Parser/blob/master/out_files/out.json)  

### Output Image
![Tree as Graph](https://github.com/ShanTen/Tree-Parser/blob/master/img_out/file_structure.png)

# NOTE:
1. This project is not complete and will not be updated for a while.
2. To use this project, you need to have [AnyTree](https://pypi.org/project/anytree/) and it's dependencies installed including dot from [graphwiz](https://graphviz.org/).  
