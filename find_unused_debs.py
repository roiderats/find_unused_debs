#!/usr/bin/env python

import datetime
import os
import subprocess
import sys
import csv

DEBUG=False
FOLLOW_SYMLINKS=False #True
OLDEST_FIRST=False
EPOCHTIME_OUTPUT=False
SHOW_PROGRESS=False
PRINT_NONFILEDEBS=False #Drops lots of metapackages, collections of symlinks

#fakelist=["adduser", "xterm", "apt", "xinit", "libjpeg8:amd64", "fonts-taml"]
# ^ ^ ^ uncomment fakelist to get a quick, result of ... fakelist - for testing

ignorelist=["AUTHORS",
            "changelog.Debian.gz", "changelog.gz",
            "copyright",
            "HISTORY", "HISTORY.gz", "HISTORY.txt", "HISTORY.txt.gz",
            "INSTALL",
            "NEWS.Debian.gz", "NEWS.gz",
            "README", "README.Debian", "README.gz", "README.md",
            "TODO", "TODO.Debian"]


dpkglist = subprocess.run( ["dpkg","-l"], capture_output=True)

if dpkglist.returncode != 0 or len(dpkglist.stderr) > 0:
    print("Something went awry, either return code or stderr:")
    print("command:", str(" ".join(dpkglist.args)))
    print("stdout:", dpkglist.stdout.decode("utf-8"))
    print("return code:", dpkglist.returncode)
    print("stderr:", dpkglist.stderr.decode("utf-8"))
    sys.exit()

list_of_dpkg_output=dpkglist.stdout.decode("utf-8").split("\n")
deblist=[]
for _ in list_of_dpkg_output:
    w=_.split()
    if len(w) == 0 or len(w[0]) != 2 or w[0][1] != "i":
        continue
    deblist.append(w[1])

try:
    deblist=fakelist
except:
    pass

if DEBUG:
    print("len(deblist):", len(deblist))

for debnr, debname in enumerate(deblist):
    _ = subprocess.run( ["dpkg","-L", debname], capture_output=True)
    rawlist = _.stdout.decode("utf-8").split("\n")
    stamp=0
    hasfiles=False
    '''
    isfile	islink	follow	is_interesting
    0		0		0		0
    1		0		0		1
    1		1		0		0
    1		0		1		1
    1		1		1		1
    '''
    for f in rawlist:
        try:
            basename=f.rsplit("/",1)[1]
        except:
            basename=""

        ignored=basename in ignorelist
        file_or_symlink=os.path.isfile(f) or (os.path.isfile(f) and FOLLOW_SYMLINKS)

        if file_or_symlink and not ignored:
            hasfiles=True
            _ = os.path.getatime(f)
        else:
            _ = 0
        stamp = _ if _ > stamp else stamp
        if DEBUG:
            print( str(datetime.datetime.fromtimestamp(stamp))
                + " " + str(stamp)
                + " " + f)
    if EPOCHTIME_OUTPUT:
        datestr=str(stamp)
    else:
        datestr=str(datetime.datetime.fromtimestamp(stamp))
    deblist[debnr]=[debname, datestr, hasfiles]
    if SHOW_PROGRESS:
        if debnr % 100 == 0 or debnr == len(deblist) - 1:
            print(str(debnr + 1) + "/" + str(len(deblist)) + ": " + debname + " " + datestr, flush=True)
            #sys.stdout.flush()

deblist=sorted(deblist, key=lambda x: x[1], reverse=not OLDEST_FIRST)

if SHOW_PROGRESS:
    print("")

writer=csv.writer(sys.stdout, dialect="unix")
writer.writerow(["deb name", "timestamp", "has real unignored files"])
for r in deblist:
    if r[2] or PRINT_NONFILEDEBS:
        writer.writerow(r)

