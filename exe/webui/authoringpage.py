# ===========================================================================
# eXe 
# Copyright 2004-2006, University of Auckland
# Copyright 2006-2007 eXe Project, New Zealand Tertiary Education Commission
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# ===========================================================================
"""
AuthoringPage is responsible for creating the XHTML for the authoring
area of the eXe web user interface.  
"""
import os
import logging
from twisted.web.resource    import Resource
from exe.webui               import common
from cgi                     import escape
import exe.webui.builtinblocks
from exe.webui.blockfactory  import g_blockFactory
from exe.engine.error        import Error
from exe.webui.renderable    import RenderableResource
from exe.engine.path         import Path
from exe                     import globals as G

from exe.webui                  import preferencespage
from exe.engine.idevice         import Idevice

log = logging.getLogger(__name__)

# ===========================================================================
class AuthoringPage(RenderableResource):
    """
    AuthoringPage is responsible for creating the XHTML for the authoring
    area of the eXe web user interface.  
    """
    name = u'authoring'

    def __init__(self, parent):
        """
        Initialize
        'parent' is our MainPage instance that created us
        """
        RenderableResource.__init__(self, parent)
        self.blocks  = []

    def getChild(self, name, request):
        """
        Try and find the child for the name given
        """
        if name == "":
            return self
        else:
            return Resource.getChild(self, name, request)


    def _process(self, request):
        """
        Delegates processing of args to blocks
        """  
        # Still need to call parent (mainpage.py) process
        # because the idevice pane needs to know that new idevices have been
        # added/edited..
        self.parent.process(request)
        if ("action" in request.args and 
            request.args["action"][0] == u"saveChange"):
            log.debug(u"process savachange:::::")
            self.package.save()
            log.debug(u"package name: " + self.package.name)
        for block in self.blocks:
            block.process(request)
        # now that each block and corresponding elements have been processed,
        # it's finally safe to remove any images/etc which made it into 
        # tinyMCE's previews directory, as they have now had their 
        # corresponding resources created:
        webDir     = Path(G.application.tempWebDir) 
        previewDir  = webDir.joinpath('previews')
        for root, dirs, files in os.walk(previewDir, topdown=False): 
            for name in files: 
                os.remove(os.path.join(root, name))

        log.debug(u"After authoringPage process" + repr(request.args))

    def render_GET(self, request=None):
        """
        Returns an XHTML string for viewing this page
        if 'request' is not passed, will generate psedo/debug html
        """
        log.debug(u"render_GET "+repr(request))

        if request is not None:
            # Process args
            for key, value in request.args.items():
                request.args[key] = [unicode(value[0], 'utf8')]
            self._process(request)

        topNode     = self.package.currentNode
        self.blocks = []
        self.__addBlocks(topNode)
        html  = self.__renderHeader()
        html += u'<body onload="onLoadHandler();">\n'
        html += u"<form method=\"post\" "

        if request is None:
            html += u'action="NO_ACTION"'
        else:
            html += u"action=\""+request.path+"#currentBlock\""
        html += u" id=\"contentForm\">"
        html += u'<div id="main">\n'
        html += common.hiddenField(u"action")
        html += common.hiddenField(u"object")
        html += common.hiddenField(u"isChanged", u"0")
        html += u'<!-- start authoring page -->\n'
        html += u'<div id="nodeDecoration">\n'
        html += u'<h1 id="nodeTitle">\n'
        html += escape(topNode.titleLong)
        html += u'</h1>\n'
        html += u'</div>\n'

        for block in self.blocks:
            html += block.render(self.package.style)

        html += u'</div>\n'
        html += u'<script type="text/javascript">$exeAuthoring.ready()</script>'
#modifications by lernmodule.net
        html += u'</form>\n'
        html += u'<div id=\"lmsubmit\"></div><script type=\"text/javascript\" language=\"javascript\">doStart();</script>\n'
#end modification
        html += common.footer()

        html = html.encode('utf8')
        return html

    render_POST = render_GET


    def __renderHeader(self):
		#TinyMCE lang (user preference)
        myPreferencesPage = preferencespage.PreferencesPage(self)
        
        """Generates the header for AuthoringPage"""
        html  = common.docType()
        #################################################################################
        #################################################################################
        
        html += u'<html xmlns="http://www.w3.org/1999/xhtml" lang="'+myPreferencesPage.getSelectedLanguage()+'">\n'
        html += u'<head>\n'
        html += u"<link rel=\"stylesheet\" type=\"text/css\" href=\"/css/exe.css\" />"
        html += u"<link rel=\"stylesheet\" type=\"text/css\" href=\"/style/base.css\" />"
        html += u"<link rel=\"stylesheet\" type=\"text/css\" href=\"/style/%s/content.css\" />" % self.package.style
        if G.application.config.assumeMediaPlugins: 
            html += u"<script type=\"text/javascript\">var exe_assume_media_plugins = true;</script>\n"
        #JR: anado una variable con el estilo
        estilo = u'/style/%s/content.css' % self.package.style	
        html += u"<script type=\"text/javascript\">var exe_style = '%s';</script>\n" % estilo
        html += u"<script type=\"text/javascript\">var exe_package_name='"+self.package.name+"';</script>\n"
        html += u'<script type="text/javascript" src="/scripts/exe_lightbox.js"></script>\n'
        html += u'<script type="text/javascript" src="/scripts/common.js">'
        html += u'</script>\n'
#modification by lernmodule.net
        html += u'<script type="text/javascript" src="/scripts/lernmodule_net.js">'
        html += u'</script>\n'
#end modification
        html += u'<script type="text/javascript" src="/scripts/authoring.js"></script>\n'
        html += '<script type="text/javascript">document.write(unescape("%3Cscript src=\'" + eXeLearning_settings.wysiwyg_path + "\' type=\'text/javascript\'%3E%3C/script%3E"));</script>';
        html += '<script type="text/javascript">document.write(unescape("%3Cscript src=\'" + eXeLearning_settings.wysiwyg_settings_path + "\' type=\'text/javascript\'%3E%3C/script%3E"));</script>';
        html += u'<script type="text/javascript" src="/scripts/libot_drag.js">'
        html += u'</script>\n'
        html += u'<title>"+_("eXe : elearning XHTML editor")+"</title>\n'
        html += u'<meta http-equiv="content-type" content="text/html; '
        html += u' charset=UTF-8" />\n'
        html += u'</head>\n'
        return html


    def __addBlocks(self, node):
        """
        Add All the blocks for the currently selected node
        """
        for idevice in node.idevices:
            block = g_blockFactory.createBlock(self, idevice)
            if not block:
                log.critical(u"Unable to render iDevice.")
                raise Error(u"Unable to render iDevice.")
            self.blocks.append(block)

# ===========================================================================
