#!/usr/bin/python3

##
# Copyright 2014, Aurel Wildfellner.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#


import os
import sys
import getpass
import re
import gnupg


def putIntoPrimarySelection(s):
    """ Uses xsel to put a string into the primary selection. """
    # escaping
    s = re.escape(s) 
    os.system('echo -n "' + s + '" | xsel -i')



def decryptFile(filename, passphrase):
    """Returns a tupple (OK, data)"""
    gpg = gnupg.GPG()

    try:
        ef = open(filename, mode="rb")
        df = gpg.decrypt_file(ef, passphrase=passphrase)
        ef.close
    except:
        return (False, "File Error!")
    finally:
       ef.close()

    if df.ok:
        s = df.data.decode("utf-8")
        return (True, s)
    else:
        return (False, "Encryption Error!")




class PasswordFileParser(object):

    def __init__(self, data):
        self.data = data
        self.passEntries = []


    def parse(self):
        lines = self.data.split("\n")

        for line in lines:
            # get lines which include a @pass
            pass_s = line.split("@pass")
            if len(pass_s) == 2:
                self.addPassEntry(pass_s[1])


    def addPassEntry(self, pl):
        # the last column on the line is the password
        passw = pl.split(" ")[-1:][0]
        # strip password from line
        pl = pl[:-len(passw)]
        self.passEntries.append((pl, passw))


    def searchEntry(self, tag):
        results = []
        for entry in self.passEntries:
            if tag in entry[0]:
                results.append(entry)
        return results



def resultMenu(results):
    while True:
        for i, result in enumerate(results):
            print(str(i) + ": " + result[0])
        print("# ", end="")
        inp = input()
        menu_items = [str(x) for x in list(range(len(results)))]
        if inp in menu_items:
            # the password from the result set
            return results[menu_items.index(inp)][1]
            break


def printHelp():
    print("pwg FILE [TAG]")


def main(): 

    if len(sys.argv) < 2:
        printHelp()
        exit(1)

    filep = sys.argv[1]
    if not os.path.isfile(filep):
        printHelp()
        exit(1)

    # match all lines if no tag provided
    tag = ""
    if len(sys.argv) > 2:
        tag = sys.argv[2]

    # get the password from stdin
    keypass = getpass.getpass()

    # decrypt the file
    eret = decryptFile(filep, keypass)
    if not eret[0]:
        print(eret[1])
        exit(1)
    decdata = eret[1]

    ### parse and search for the tag
    parser = PasswordFileParser(decdata)
    parser.parse()
    results = parser.searchEntry(tag)

    ### select the right search result
    passw = ""
    if len(results) > 1:
        passw = resultMenu(results)
    elif len(results) == 1:
        info = results[0][0]
        if info not in ["", " "]:
            print("Selecting password for: " + results[0][0])
        passw = results[0][1]
    else:
        print("Nothing found.")
        exit(1)

    putIntoPrimarySelection(passw)



if __name__ == "__main__":
    main()

