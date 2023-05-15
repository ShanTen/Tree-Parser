TknEntry = "<TreeStart>" # Token for the start of the tree
TknExit = "<TreeEnd>" # Token for the end of the tree

TknObjectIndent = "+---" #Object may contain other objects (folder) or may be a single entity (file)
TknObjectExit = "\---" #Object is the last in the list

TknCommentChar = "#"

TknIndent = "|   "

TknRootStartChar = "["
TknRootEndChar = "]"

###############################################################################################################################

from ParentErrorClass import ParentErrorClass

class IllegalCharacterError(ParentErrorClass):
    def __init__(self, details):
        super().__init__("Illegal Character", details)

class RootNotClosedError(ParentErrorClass):
    def __init__(self, details):
        super().__init__("Root Not Closed", details)

###############################################################################################################################

class Token:
    def __init__(self, type, value, line, indent_level, isFinalIndent=False):
        self.type = type
        self.value = value
        self.lineNumber = line
        self.indentLevel = indent_level
        self.isFinalIndent = isFinalIndent

    #this function is going to so so useful
    def set_as_final_indent(self):
        self.isFinalIndent = True

    def __repr__(self):
        return f"Token({self.type}, '{self.value}', {self.lineNumber}, {self.indentLevel}, {self.isFinalIndent})"

###############################################################################################################################

class Lexer:
    def __init__(self, text):
        self.text = text
        self.lines = text.split('\n')
        self.numberOfLines = len(self.lines)
        self.isEoF = False

        self.currentLine = -1
        self.pos = -1

        self.currentChar = None
        self.advance_line()

    def __peek_to_EoL_and_return_string(self):
        #starting from the current position, skip to the end of the line and return the string
        #includes current position
        __str =  self.lines[self.currentLine][self.pos:]
        return __str

    def __skip_to_EoL_and_return_string(self):
        #starting from the current position, skip to the end of the line and return the string
        #includes current position
        __str = ""
        while 1:
            if self.currentChar == None:
                break
            __str += self.currentChar
            self.advance_char()
        return __str

    def __get_comment_from_objStr(self, obj_str:str) -> str:
        if TknCommentChar in obj_str:
            comment_char_index = obj_str.index(TknCommentChar)
            __commentStr = obj_str[comment_char_index:].strip()
            return __commentStr
        else:
            return None
        
    def __handle_comments_and_return_token(self):
        __line = self.currentLine
        eol_string = self.__skip_to_EoL_and_return_string()
        comment = self.__get_comment_from_objStr(eol_string)
        if comment != None:
            comment = comment[1:] #remove the comment char (#)
            return Token("COMMENT", comment, __line, None, False)
        return None

    def advance_line(self):
        self.currentLine += 1
        self.pos = -1
        self.advance_char()

    def advance_char(self):
        self.pos += 1

        if self.pos >= len(self.lines[self.currentLine]):
            self.currentChar = None #When we hit the end of a line, we set the currentChar to None but we do not change the line here
            #power to change a line lies outside advance_char()
        else:
            self.currentChar = self.lines[self.currentLine][self.pos]

    def peek(self, n):        
        guess_str = self.lines[self.currentLine][self.pos: self.pos+n]
        return guess_str

    def __get_object_type(self, object_name):
        #TODO: Add the forced declaration rule here

        if "." in object_name:
            return "FILE"
        else:
            return "DIR"

    def tokenize(self):
        tokens = []
        __indentLevel = 0

        while self.currentLine < self.numberOfLines:

            #Debug
            # print(tokens)
            # print(f"{self.currentChar} == {TknObjectIndent}: ", self.currentChar == TknObjectIndent)
            # input(f"Current Char: {self.currentChar}")


            if self.currentChar == None:
                self.advance_char()

            elif self.currentChar in ' \t':
                self.advance_char()

            elif self.currentChar == '\n':
                self.advance_line()
                self.advance_char()

            elif self.currentChar == TknCommentChar:
                __commentStr = self.__skip_to_EoL_and_return_string()
                __commentStr = __commentStr[1:] #remove hash
                tokens.append(Token("COMMENT", __commentStr, self.currentLine, None))
                self.advance_line()

            elif self.currentChar == "<" :
                if self.peek(len(TknEntry)) == TknEntry:
                    tokens.append(Token("ENTRY", TknEntry, self.currentLine, None)) #hack because we are directly using TknEntry instead of collecting the value
                    #technically speaking should skip the next line by advancing each character in the line until the next line
                    __comment_token = self.__handle_comments_and_return_token()
                    if __comment_token != None:
                        tokens.append(__comment_token)
                    self.advance_line()

                elif self.peek(len(TknExit)) == TknExit:
                    tokens.append(Token("EXIT", TknExit, self.currentLine, None)) #hack
                    __comment_token = self.__handle_comments_and_return_token()
                    if __comment_token != None:
                        tokens.append(__comment_token)
                    
                    return '', tokens
                
                else:
                    #technically 'should'go on until it hits an invalid character or EoL
                    self.advance_char()                    

            elif self.currentChar == TknRootStartChar:
                __rootValue = "" 

                #this is kinda cheating I know
                eol = self.__peek_to_EoL_and_return_string()
                # print(eol)
                if TknRootEndChar not in eol:
                    return "ERR", RootNotClosedError(f"Folder root not closed on line {self.currentLine+1}.")


                while self.currentChar != TknRootEndChar:
                    # print("We are in the loop for detecting end root token")
                    self.advance_char()
                    __rootValue += self.currentChar
                    #TODO: Add a check for EoL 
                #At this point we have hit End Root Token or are in an infinite loop (how to fix this -- add a check for EoL.)
                else:
                    __rootValue = __rootValue[:-1].strip() #remove the last character which is the TknRootEndChar
                    tokens.append(Token("ROOT", __rootValue, self.currentLine, __indentLevel))
                    __comment_token = self.__handle_comments_and_return_token()
                    if __comment_token != None:
                        tokens.append(__comment_token)
                    self.advance_line() #reset to new line

            #universal parsing for all "TknObjectIndent" (is it an object? check) 
            elif self.currentChar == TknObjectIndent[0] or self.currentChar == TknIndent[0]:
                __objectName = ""
                __isFinalIndent = False
                __indentLevel = 0 #because we are in a new line each time (put this in new_line setter in a bit)
                __have_i_hit_an_object = False

                while not __have_i_hit_an_object:

                    if self.peek(len(TknIndent)) == TknIndent:
                        __indentLevel += 1
                        for _ in range(len(TknIndent)): 
                            self.advance_char()

                        #white space sanity check
                        while self.currentChar == ' ' or self.currentChar == '\t':
                            self.advance_char()

                        #Only move it exactly by the length of the indent token
                        #Most unstable shit because nobody could ever even think of parsing bad data
                        #TODO: Space check here please I cannot stress this enough
                        #TODO: Add a check for indentation errors 

                    if self.peek(len(TknObjectIndent)) == TknObjectIndent:
                        __indentLevel += 1

                        for _ in range(len(TknObjectIndent)): #Sanity Explanation: -1 because we already have the first character
                            self.advance_char()

                        #How we'll go to EoL is by literally abusing python's array slicing
                        #For all cases of an Object indent, there is always an object at the end be it a dir or a file
                        #we are now going to tokenize the object name

                        __objectName = self.lines[self.currentLine][self.pos:] #straight up hack - take all chars till EoL 
                        __objectName = __objectName.strip() #remove all leading and trailing whitespaces

                        __objectType = self.__get_object_type(__objectName)

                        __comment_token = None
                        if TknCommentChar in __objectName:
                            __comment_token_index = __objectName.index(TknCommentChar)
                            __comment = __objectName[__comment_token_index:]
                            __comment = __comment[1:] #remove hash
                            __comment_token = Token("COMMENT", __comment, self.currentLine, None, False)
                            __objectName = __objectName[:__comment_token_index]
                            __objectName = __objectName.strip() #remove all leading and trailing whitespaces

                        if __objectName[-1] == "/" or __objectName[-1] == "\\": #escape character it's not actually 2 chars long
                            __objectName = __objectName[:-1]

                        tokens.append(Token(__objectType, __objectName, self.currentLine, __indentLevel, __isFinalIndent))
                        if __comment_token:
                            tokens.append(__comment_token)

                        __have_i_hit_an_object = True
                        self.advance_line() #reset to new line

                    elif self.peek(len(TknObjectExit)) == TknObjectExit:

                        # print("Got a hit for exit token detection")

                        #I know this can be written better but this "just" works
                        #TODO: Make this better (remove the repetition)
                        __isFinalIndent = True
                        __indentLevel += 1
                        for _ in range(len(TknObjectIndent)): 
                            self.advance_char()
                        __objectName = self.lines[self.currentLine][self.pos:] 
                        __objectName = __objectName.strip() 

                        __comment_token = None
                        if TknCommentChar in __objectName:
                            __comment_token_index = __objectName.index(TknCommentChar)
                            __comment = __objectName[__comment_token_index:]
                            __comment = __comment[1:]
                            __comment_token = Token("COMMENT", __comment, self.currentLine, None, False)
                            __objectName = __objectName[:__comment_token_index]
                            __objectName = __objectName.strip() #remove all leading and trailing whitespaces

                        if __objectName[-1] == "/" or __objectName[-1] == "\\": #escape character it's not actually 2 chars long
                            __objectName = __objectName[:-1]

                        tokens.append(Token(self.__get_object_type(__objectName), __objectName, self.currentLine, __indentLevel, __isFinalIndent))

                        if __comment_token:
                            tokens.append(__comment_token)
                        
                        __have_i_hit_an_object = True
                        self.advance_line() #reset to new line
                
            elif self.currentChar == TknObjectExit[0]:
                if self.peek(len(TknObjectExit)) == TknObjectExit:
                    # print("Got a hit for exit token detection")
                    __isFinalIndent = True
                    __indentLevel = 1
                    for _ in range(len(TknObjectIndent)): 
                        self.advance_char()
                    __objectName = self.lines[self.currentLine][self.pos:] 

                    __comment_token = None
                    if TknCommentChar in __objectName:
                        __comment_token_index = __objectName.index(TknCommentChar)
                        __comment = __objectName[__comment_token_index:]
                        __comment = __comment[1:]
                        __comment_token = Token("COMMENT", __comment, self.currentLine, None, False)
                        __objectName = __objectName[:__comment_token_index]
                        __objectName = __objectName.strip() #remove all leading and trailing whitespaces
                        
                    if __objectName[-1] == "/" or __objectName[-1] == "\\": #escape character it's not actually 2 chars long
                            __objectName = __objectName[:-1]
                            __objectName = __objectName.strip() 
                    
                    tokens.append(Token(self.__get_object_type(__objectName), __objectName, self.currentLine, __indentLevel, __isFinalIndent))

                    if __comment_token:
                        tokens.append(__comment_token)                        

                    self.advance_line() #reset to new line
                else:
                    return "ERR", IllegalCharacterError(f"Illegal character '{self.currentChar}' on line {self.currentLine + 1} at position {self.pos + 1}")

            else:
                return "ERR", IllegalCharacterError(f"Illegal character '{self.currentChar}' on line {self.currentLine + 1} at position {self.pos + 1}")
        
        return "",tokens

###############################################################################################################################

def testRun():
    with open("testTree.tree", "r") as f:
        text = f.read()

    lexer = Lexer(text)
    resTuple = lexer.tokenize()
    if resTuple[0] == "ERR":
        print(resTuple[1].stringify())
    else:
        tokens = resTuple[1]
        print("Tokens:")
        print(tokens)
