#!C:\Python27\python

# specify any options necessary when building installers
nsis_options = ''

# if makensis.exe is not in your PATH, specify explicit pathname here
nsis = 'c:\Program Files\NSIS\makensis.exe'

# name used for temporary file that contains branded splash screen
BRANDED_JPG = 'splashb.jpg'

import sys
import os
import shutil
import subprocess
import Image, ImageFont, ImageDraw

# clean out the build and dist dirs
os.chdir('../..'); WDIR = os.getcwd()
shutil.rmtree('build', True)
shutil.rmtree('dist', True)

# copy Firefox into the dist tree
shutil.copytree('exe/webui/Mozilla Firefox', 'dist/Mozilla Firefox')

# build the executable
subprocess.check_call('c:\Python27\python win-setup.py py2exe', shell = True, cwd = WDIR)

# get the version
sys.path.insert(0, WDIR)
from exe.engine import version

versions = "/DEXE_VERSION=%s /DEXE_REVISION=%s /DEXE_SPLASH=%s" \
        % (version.release, version.revision, BRANDED_JPG)
# for specific branches use 
#versions = "/DEXE_VERSION=%s /DEXE_REVISION=%s /DEXE_SPLASH=%s" \
#        % (version.project+"-"+version.release, version.revision, BRANDED_JPG)

# brand the splash screen
os.chdir(os.path.join(WDIR, 'installs/windows'))
font = ImageFont.truetype("arial.ttf", 12)
fontcolor = '#808080'
(w, h) = font.getsize("Version:")
im = Image.open("splash1.jpg")
draw = ImageDraw.Draw(im)
draw.text((148, 102), "Project: " + version.project, font=font,
        fill=fontcolor)
draw.text((148, 116), "Version: " + version.release, font=font,
        fill=fontcolor)
draw.text((148, 130), "Revision: " + version.revision,
        font=font, fill=fontcolor)
del draw
im.save(BRANDED_JPG)

# make the installers
for installer in ('exe.nsi', 'exe.standalone.nsi'):
    try:
        pnsis = subprocess.Popen('%s %s %s %s' %
                                 ('makensis', nsis_options, versions, installer))
    except OSError:
        try:
            pnsis = subprocess.Popen('%s %s %s %s' %
                                     (nsis, nsis_options, versions, installer))
        except OSError:
            print '*** unable to run makensis, check PATH or explicit pathname'
            print '    in make.py'
    pnsis.wait()

# remove branded splash screen
os.remove(BRANDED_JPG)
