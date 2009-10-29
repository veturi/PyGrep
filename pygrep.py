#!/usr/bin/env python
""" PythonGrep (PyGrep) version 0.001901185 alpha
Maintained by Jarno Tikka
jarno.tikka@gmail.com

PythonGrep works the same way classic grep does (tho much more
simplified and with less functionality) but provides all the regular
expression patterns available in Python.

Usage:
pygrep [OPTIONS] PATTERN [FILE...]

Options:
    -i --ignore-case: Distinctions in both the pattern and the input files.
    -v --invert-match: Inverts the sense of matching, to select non-matching 
       lines.
    -w --word-regexp: Select only those lines containing matches that form 
       whole words.
    -o --only-matching: Print only the matched (non-empty) parts of a matching 
       line, with each such part on a separate output line.
    -C NUM --Context=NUM : Print NUM lines of output context. With the -o 
       option this has no effect and a warning is given.
    -h --help: Prints help and instructions for user

Options and descriptions are from classic grep's manual so props goes
for the original authors!

Exit status is 0 if no errors occurred.
Exit status is 1 if error occurred during execution.

protip: Try creating alias like alias pygrep="~/./pygrep.py" for more user
friendly usage.
"""

import sys
import os
import re
import getopt
import select


class pygrepOptions(object):
    """This class contains all predefined variables required by PyGrep."""
    def __init__(self):
        #option variables
        self.ignoreCase = False
        self.invertMatch = False
        self.onlyMatching = False
        self.context = False
        self.contextNum = 0
        #list of file objects
        self.fileList = []
        #accepted options without
        self.shortOptions = "ivwoC:h"
        self.longOptions = ["ignore-case", "invert-match", "word-regexp" \
                            "only-matching", "Context=", "help"]


def grep(pattern, pg):
    """Search through given file(s) and/or standard input for matching patterns.
    Prints lines matching the pattern with given options.
    Gets two arguments:
    'pattern' - Regular expression pattern
    'pg' - instance of pygrepOptions class.
    returns 0 on successful execution
    """
    outputCount = 0
    
    if pg.ignoreCase:
        rePattern = re.compile(r'%s' % pattern, re.I)
    else:
        rePattern = re.compile(r'%s' % pattern)
    
    for file in pg.fileList:
        print "File: %s" % file.name
        for line in file:
            #don't accept empty lines
            if not line.strip():
                continue
            reObject = rePattern.search(line)
            #if line matched and invert-match options is set to False
            if reObject and not pg.invertMatch:
                #if option -C is set and enough lines are printed
                if pg.context and int(outputCount) == int(pg.contextNum):
                    break
                #if only-matching option is set, print only matching word
                if pg.onlyMatching:
                    print reObject.group(0)
                else:
                    print line.strip('\n')
                    outputCount += 1
            #if line didn't match and invert-match option is set to True
            elif not reObject and pg.invertMatch:
                #if option -C is set and enough lines are printed
                if pg.context and int(outputCount) == int(pg.contextNum):
                    break
                #if only-matching options is set, print only matching word
                #if pg.onlyMatching:
                #    #print reObject.group(0)
                #    print line
                else:#not pg.onlyMatching:
                    print line.strip('\n')
                    outputCount += 1
    return 0


def containsData():
    """ Check if sys.stdin is empty.
    Returns boolean value. True if not empty, False if empty.
    """
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])


def handleFiles(args, pg):
    """Handles opening given input(s).
    Binds file objects to an instance of pygrepOptions.
    Returns instance of pygrepOptions.
    
    Example 0:
    >>> pg = pygrepOptions()
    >>> x = handleFiles(["testing/test.txt"], pg)
    >>> isinstance(x, type(pg))
    True
    
    Example 1 (file doesn't exist):
    >>> pg = pygrepOptions()
    >>> handleFiles(["noFile.txt"], pg)
    Traceback (most recent call last):
    ...
    SystemExit: 1
    
    Example 2 (wrong options object):
    >>> pg = "wrongobject"
    >>> handleFiles(["testing/test.txt"], pg)
    Traceback (most recent call last):
    ...
    SystemExit: 1
    """
    if not isinstance(pg, pygrepOptions):
        sys.exit(1)
    
    if containsData():
        pg.fileList.append(sys.stdin)
    for filename in args:
        try:
            f = open(filename, 'r')
        except IOError:
            print "No file %s found!" % filename
            sys.exit(1)
        pg.fileList.append(f)
    return pg


def handleArgs(argv, pg):
    """Handles parsing and handlingoptions from given list of arguments and
    returns two different values.
    'args[0]' contains given regular expression pattern and 'pg' is 
    pygrepOptions object.
    Checks if required regexp pattern and input are given and if not
    stops execution with exit value of 1.
    
    Unit tests:
    
    Example 0:
    >>> pg = pygrepOptions()
    >>> x,y = handleArgs(["-v", "pattern", "testing/test.txt"], pg)
    >>> x == "pattern" and isinstance(y, type(pg))
    True
    
    Example 1 (empty arguments list given):
    >>> handleArgs([], pygrepOptions())
    Traceback (most recent call last):
    ...
    SystemExit: 1
    
    Example 2 (no pattern given):
    >>> handleArgs(["-v"], pygrepOptions())
    Traceback (most recent call last):
    ...
    SystemExit: 1
    
    Example 3 (wrong option P in args):
    >>> handleArgs(["-vP", "pattern", "/tests/test.txt"], pygrepOptions())
    Traceback (most recent call last):
    ...
    GetoptError: option -P not recognized
    
    Example 4 (no input given):
    >>> handleArgs(["-v", "pattern"], pygrepOptions())
    Traceback (most recent call last):
    ...
    SystemExit: 1
    
    Example 5 (false options object):
    >>> handleArgs(["-v", "pattern", "testfile.txt"], 'falseObject')
    Traceback (most recent call last):
    ...
    SystemExit: 1
    """
    if not isinstance(pg, pygrepOptions):
        sys.exit(1)
    
    opts, args = getopt.getopt(argv, pg.shortOptions, pg.longOptions)
    
    #Handle given options.
    for option, value in opts:
        if option in ["-h", "--help"]:
            help()
            sys.exit(0)
        if option in ["-i","--ignore-case"]:
            pg.ignoreCase = True
        if option in ["-v","--invert-match"]:
            pg.invertMatch = True
        if option in ["-w","--word-regexp"]:
            args[0] = "\\b%s\\b" % args[0]
        if option in ["-C","--Context"]:
            pg.context = True
            pg.contextNum = int(value)
        if option in ["-o","--only-matching"]:
            pg.onlyMatching = True
    
    #If user gave both -o and -C options, print warning for user
    #and ignore -C option setting it to False
    if pg.onlyMatching and pg.context:
        print "-o and -C are both enabled. -C isn't allowed with -o option!"
        print "Ignoring -C"
        print "Press any key to continue!"
        pg.context = False
        sys.stdin.readline()
    
    #Check if required regexp pattern and input are given.
    if len(args) == 0:
        print "No pattern given! Please define a pattern to search for."
        sys.exit(1)
    elif len(args) == 1:
        if not containsData():
            print "No input file(s) or standard input given!"
            print "Use %s -h or --help for instructions." % sys.argv[0]
            sys.exit(1)
            
    pg = handleFiles(args[1:], pg)
    
    return args[0], pg


def main(argv):
    """ Main method for PyGrep. Controls flow of program when called
    as main module.
    Receives list of arguments as argument 'argv'    
    """
    pg = pygrepOptions()
    pattern, pg = handleArgs(argv, pg)
    
    return grep(pattern, pg)
    

def help():
    """Prints instructions to user."""
    print """\nUsage:
    %s [OPTIONS] PATTERN [FILE...]

Options:
    -i --ignore-case: Distinctions in both the pattern and the input files.
    -v --invert-match: Inverts the sense of matching, to select non-matching 
       lines.
    -w --word-regexp: Select only those lines containing matches that form 
       whole words.
    -o --only-matching: Print only the matched (non-empty) parts of a matching 
       line, with each such part on a separate output line.
    -C NUM --Context=NUM : Print NUM lines of output context. With the -o 
       option this has no effect and a warning is given.
    -h --help: Prints help and instructions for user
    """ % sys.argv[0]


#Main entry point for application if used as main program
#Calls main-method which controls flow of PyGrep with given arguments
if __name__ == "__main__":
    import doctest
    doctest.testmod()
    args = sys.argv[1:]
    sys.exit(main(args))
