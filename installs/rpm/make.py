#!/usr/bin/env python

# another thinly disguised shell script written in Python

import sys
import os
import glob
import subprocess

# TOPDIR root of RPM build tree typically /usr/src/redhat or /home/xxx/.rpm
#TOPDIR = '/usr/src/redhat'
TOPDIR = os.path.join(os.environ['HOME'], '.rpm')

# where the SVN exe source directory is
#SRCDIR = '/usr/local/src'
SRCDIR = os.path.abspath('../../..')

# this is done in a way consistent with the other builds...
#   even though we have the info without doing the import
REVISION_FILE = os.path.join(SRCDIR, 'exe/exe/engine/version_svn.py')
os.chdir(os.path.join(SRCDIR, 'exe'))

sys.path.insert(0, os.path.join(SRCDIR, 'exe'))
from exe.engine import version

try:
    line = open('debian/changelog').readline()
    build = line.split(':')[1].split(')')[0]
    revision = build.split(version.release + ".")[1]
    open(REVISION_FILE, 'wt').write('revision = "%s"\n' % revision)
except OSError:
    print "*** Warning: 'svnversion' tool not available to update revision number"

# find the first release that doesn't exist
clrelease = 1
while 1:
    files = glob.glob(os.path.join(TOPDIR, 'RPMS/i386',
        'exe-%s-%d.*.i386.rpm' % (build, clrelease)))
    if len(files) == 0:
        break
    clrelease += 1

print "Making version: %s release: %s" % (build, clrelease)

# create the source tarball
os.chdir(SRCDIR)
tarball = os.path.join(TOPDIR, 'SOURCES', 'exe-' + build + '-source.tgz')
try:
    ret = subprocess.call('tar -czf %s --wildcards-match-slash --exclude=".git" --exclude="*.svn*" --exclude "*.pyc" --exclude="*.tmp" --exclude="*~" --exclude="dist/*" --exclude="build/*" --exclude="pyxpcom/*" exe' %
                              tarball, shell = True)
    if ret < 0:
	print >>sys.stderr, "Unable to make tarball signal", -ret
	sys.exit(ret)
except OSError, e:
    print >>sys.stderr, "Execution of tar failed:", e

try:
    ret = subprocess.call('rpmbuild -tb --define="clversion %s" --define="clrelease %s" %s' % 
                          (build, clrelease, tarball), shell = True)
    if ret < 0:
        print >>sys.stderr, "Unable to run rpmbuild, signal", -ret
        sys.exit(ret)
except OSError, e:
    print >>sys.stderr, "Execution of rpmbuild failed:", e

