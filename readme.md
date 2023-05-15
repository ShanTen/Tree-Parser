# Serialized Tree Parser

Converts mark up in the form of a an ascii tree into an iterable.

## Objective
- I have some data in a text file, it looks like a tree. 
- I wanted to convert this data into a tree structure in memory and iterate it.
- Maybe even re-create original file/folder structure as an empty file

### Objective In Detail
Assuming I have a file like this (serialized data)

```
...
[Heading] 
|--- geography
|   |--- countries
|   |--- seas
|   |   |--- indian_ocean
|   |   |--- pacific_ocean
|   |   \--- atlantic_ocean
...
```

I wanted to make this into an object which I can iterate later (hierarchial data).  

## Design
+ Based of simple to grasp syntax
+ Refer Lexer.py and Parser.py
+ Uses [AnyTree](https://pypi.org/project/anytree/) for the tree iterable.

## Issues
+ Better error handling
+ Ironing out bugs 
+ Built originally to replicate file trees and not as a general purpose ML
