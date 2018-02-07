'''
Program to modify the extension names for a file or directory to .dcm
Hillary Elrick
CISC 499
Jan 22, 2018
'''
#TODO: add cases for preexisting file extension, and optional printout of the files changed, also get it to ignore the .DS_Store files
import os
from os.path import join
def main():
    path = input("Please enter the file or directory path: ")
    for root, dirs, files in os.walk(path):
        for name in files:
            newname = name + ".dcm"
            newname = join(root, newname)
            os.rename(join(root,name), newname)


main()

