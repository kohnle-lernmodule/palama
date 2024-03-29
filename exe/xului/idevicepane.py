# ===========================================================================
# eXe 
# Copyright 2004-2005, University of Auckland
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
IdevicePane is responsible for creating the XHTML for iDevice links
"""

import logging
from exe.webui.renderable import Renderable
from exe import globals as G
from nevow import stan
import cgi

log = logging.getLogger(__name__)

# ===========================================================================
class IdevicePane(Renderable):
    """
    IdevicePane is responsible for creating the XHTML for iDevice links
    """
    name = 'idevicePane'

    def __init__(self, parent):
        """ 
        Initialize
        """ 
        Renderable.__init__(self, parent)
        self.client = None
        log.debug("Load appropriate iDevices")
        self.prototypes = {}
        self.ideviceStore.register(self)
        for prototype in self.ideviceStore.getIdevices():
            log.debug("add "+prototype.title)
            self.prototypes[prototype.id] = prototype


    def process(self, request):
        """ 
        Process the request arguments to see if we're supposed to 
        add an iDevice
        """
        log.debug("Process" + repr(request.args))
        if ("action" in request.args and 
            request.args["action"][0] == "AddIdevice"):

            self.package.isChanged = True
            prototype = self.prototypes.get(request.args["object"][0])
            if prototype:
                self.package.currentNode.addIdevice(prototype.clone())

            
    def addIdevice(self, idevice):
        """
        Adds an iDevice to the pane
        """
        log.debug("addIdevice id="+idevice.id+", title="+idevice.title)
        self.prototypes[idevice.id] = idevice
        self.client.call('XHAddIdeviceListItem', idevice.id, idevice.title)


    def delIdevice(self, idevice):
        """
        Delete an iDevice from pane
        """
        log.debug("delIdevice id="+idevice.id+", title="+idevice.title)
        self.prototypes.pop(idevice.id, 0)
        self.client.call('XHDelIdeviceListItem', idevice.title)


    def render(self, ctx, data):
        """
        Returns an html string for viewing this pane
        """
        # Create a scecial server side func that the 
        # Idevice editor js can call
        #addHandler = handler(self.handleAddIdevice,
        #                     identifier='outlinePane.handleAddIdevice')
        # The below call stores the handler so we can call it
        # as a server 
        #addHandler(ctx, data) 

        # Now do the rendering
        log.debug("Render")

        html  = u"<!-- IDevice Pane Start -->\n"
        html += u"<listbox id=\"ideviceList\" flex=\"1\" "
        html += u"style=\"background-color: #FFF;\">\n"

        prototypes = self.prototypes.values()
        def sortfunc(pt1, pt2):
            """Used to sort prototypes by title"""
            return cmp(pt1.title, pt2.title)
        prototypes.sort(sortfunc)
        for prototype in prototypes:
            if prototype._title.lower() not in G.application.config.hiddeniDevices \
            and prototype._title.lower() \
            not in G.application.config.deprecatediDevices:
                html += self.__renderPrototype(prototype)

        html += u"</listbox>\n"
        html += u"<!-- IDevice Pane End -->\n"
        return stan.xml(html.encode('utf8'))


    def __renderPrototype(self, prototype):
        """
        Add the list item for an iDevice prototype in the iDevice pane
        """
        log.debug("Render "+prototype.title)
        log.debug("_title "+prototype._title)
        log.debug("of type "+repr(type(prototype.title)))
        xul  = u"  <listitem label=\"" + prototype.title + "\" "
        xul += u"onclick=\"submitLink('AddIdevice', "
        xul += u"'" + prototype.id + "', 1)\"/>"""
        return xul
        
    
# ===========================================================================
