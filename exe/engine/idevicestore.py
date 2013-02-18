# ===========================================================================
# eXe 
# Copyright 2004-2006, University of Auckland
# Copyright 2004-2008 eXe Project, http://eXeLearning.org/
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
The collection of iDevices available
"""

from exe.engine         import persist
from exe.engine.idevice import Idevice
from exe.engine.field   import TextAreaField, FeedbackField
from nevow.flat         import flatten

import imp
import sys
import logging
import copy

log = logging.getLogger(__name__)

# ===========================================================================
class IdeviceStore:
    """
    The collection of iDevices available
    """
    def __init__(self, config):
        """
        Initialize
        """
        self._nextIdeviceId = 0
        self.config         = config
        self.extended       = []
        self.generic        = []
        self.listeners      = []
        #JR: Anado una lista que contendra todos los iDevices disponibles
        self.factoryiDevices = []


    def getNewIdeviceId(self):
        """
        Returns an iDevice Id which is unique
        """
        id_ = unicode(self._nextIdeviceId)
        self._nextIdeviceId += 1
        return id_

    def isGeneric(self, idevice):
        """
        Devuelve true si el iDevice es de la clase GenericIdevie
        """
        from exe.engine.genericidevice import GenericIdevice
        if isinstance(idevice, GenericIdevice):
            return True
        else:
            return False
        
    def getIdevices(self):
        """
        Get the idevices which are applicable for the current node of
        this package
        In future the idevices which are returned will depend
        upon the pedagogical template we are using
        """
        return self.extended + self.generic
    
    def getFactoryIdevices(self):
        """
        JR: Devuelve todos los iDevices de fabrica
        """
        return self.factoryiDevices

    
    def __delGenericIdevice(self, idevice):
        """
        Delete a generic idevice from idevicestore.
        """
        idevice_remove = None
        exist = False
        for i in self.generic:
            if idevice.title == i.title:
                idevice_remove = i
                exist = True
                break
        if exist:
            self.generic.remove(idevice_remove)
            #JR: Comunicamos a los listener que este iDevice ya no esta disponible
            for listener in self.listeners:
                listener.delIdevice(idevice_remove)

    
    def __delExtendedIdevice(self, idevice):
        """
        Delete an extended idevice from idevicestore.
        """
        idevice_remove = None
        exist = False
        for i in self.extended:
            if idevice.title == i.title:
                idevice_remove = i
                exist = True
                break
        if exist:
            self.extended.remove(idevice_remove)
            #JR: Comunicamos a los listener que este iDevice ya no esta disponible
            for listener in self.listeners:
                listener.delIdevice(idevice_remove)
            
    def delIdevice(self, idevice):
        """
        JR: Borra un idevice
        """
        if not self.isGeneric(idevice):
            idevice_remove = None
            exist = False
            for i in self.extended:
                if i.title == idevice.title:
                    idevice_remove = i
                    exist = True
                    break
            if exist:
                self.__delExtendedIdevice(idevice_remove)
        else:
            idevice_remove = None
            exist = False
            for i in self.generic:
                if i.title == idevice.title:
                    idevice_remove = i
                    exist = True
                    break
            if exist:
                self.__delGenericIdevice(idevice_remove)
    
    def register(self, listener):
        """
        Register a listener who is interested in changes to the
        IdeviceStore.  
        Created for IdevicePanes, but could be used by other objects
        """
        self.listeners.append(listener)


    def addIdevice(self, idevice):
        """
        Register another iDevice as available
        """
        if not self.isGeneric(idevice):
            exist = False
            for i in self.extended:
                if i.title == idevice.title:
                    exist = True
            if not exist:
                self.extended.append(idevice)
                idevice.edit = True
                for listener in self.listeners:
                    listener.addIdevice(idevice)
        else:
            exist = False
            for i in self.generic:
                if i.title == idevice.title:
                    exist = True
            if not exist:
                self.generic.append(idevice)
                idevice.edit = True
                for listener in self.listeners:
                    listener.addIdevice(idevice)        

    def load(self):
        """
        Load iDevices from the generic iDevices and the extended ones
        """
        log.debug("load iDevices")
        idevicesDir = self.config.configDir/'idevices'
        if not idevicesDir.exists():
            idevicesDir.mkdir()
        self.__loadExtended()
        self.__loadGeneric()
        #JR: comunicamos a los listener los iDevices extendidos
        for listener in self.listeners:
            for idevice in self.getIdevices():
                listener.addIdevice(idevice)
    
    def __getIdevicesFPD(self):
        """
        JR: Esta funcion devuelve los iDevices de FPD
        """
        from exe.engine.reflectionfpdidevice import ReflectionfpdIdevice
        from exe.engine.reflectionfpdmodifidevice import ReflectionfpdmodifIdevice
        from exe.engine.clozefpdidevice import ClozefpdIdevice
        from exe.engine.clozelangfpdidevice import ClozelangfpdIdevice
        from exe.engine.parasabermasfpdidevice import ParasabermasfpdIdevice
        from exe.engine.debesconocerfpdidevice import DebesconocerfpdIdevice
        from exe.engine.citasparapensarfpdidevice import CitasparapensarfpdIdevice
        from exe.engine.recomendacionfpdidevice import RecomendacionfpdIdevice
        from exe.engine.verdaderofalsofpdidevice import VerdaderofalsofpdIdevice
        from exe.engine.seleccionmultiplefpdidevice import SeleccionmultiplefpdIdevice
        from exe.engine.eleccionmultiplefpdidevice import EleccionmultiplefpdIdevice
        from exe.engine.casopracticofpdidevice import CasopracticofpdIdevice
        from exe.engine.ejercicioresueltofpdidevice import EjercicioresueltofpdIdevice
        from exe.engine.destacadofpdidevice import DestacadofpdIdevice 
        from exe.engine.orientacionesalumnadofpdidevice import OrientacionesalumnadofpdIdevice
        from exe.engine.orientacionestutoriafpdidevice import OrientacionestutoriafpdIdevice
        from exe.engine.freetextfpdidevice import FreeTextfpdIdevice
        
        idevices_FPD = []
        idevices_FPD.append(ReflectionfpdIdevice())
        idevices_FPD.append(ReflectionfpdmodifIdevice())
        idevices_FPD.append(ClozefpdIdevice())
        idevices_FPD.append(ClozelangfpdIdevice())
        idevices_FPD.append(ParasabermasfpdIdevice())
        idevices_FPD.append(DebesconocerfpdIdevice())
        idevices_FPD.append(CitasparapensarfpdIdevice())
        idevices_FPD.append(RecomendacionfpdIdevice())
        idevices_FPD.append(VerdaderofalsofpdIdevice())
        idevices_FPD.append(SeleccionmultiplefpdIdevice())
        idevices_FPD.append(EleccionmultiplefpdIdevice())
        idevices_FPD.append(CasopracticofpdIdevice())
        idevices_FPD.append(EjercicioresueltofpdIdevice())
        idevices_FPD.append(DestacadofpdIdevice()) 
        #idevices_FPD.append(CorreccionfpdIdevice())
        idevices_FPD.append(OrientacionesalumnadofpdIdevice())
        idevices_FPD.append(OrientacionestutoriafpdIdevice())
        idevices_FPD.append(FreeTextfpdIdevice())
        
        return idevices_FPD


    def __getFactoryExtendediDevices(self):
        """
        JR: Carga los iDevices de fabrica
        """
        from exe.engine.freetextidevice import FreeTextIdevice
        from exe.engine.multimediaidevice import MultimediaIdevice
        from exe.engine.reflectionidevice import ReflectionIdevice
        from exe.engine.casestudyidevice import CasestudyIdevice
        from exe.engine.truefalseidevice import TrueFalseIdevice 
        # converting ImageWithTextIdevice -> FreeTextIdevice:
        #from exe.engine.imagewithtextidevice  import ImageWithTextIdevice
        #from exe.engine.wikipediaidevice import WikipediaIdevice
        from exe.engine.attachmentidevice import AttachmentIdevice
        from exe.engine.titleidevice import TitleIdevice
        from exe.engine.galleryidevice import GalleryIdevice
        from exe.engine.clozeidevice import ClozeIdevice 
        #from exe.engine.clozelangidevice          import ClozelangIdevice
        from exe.engine.flashwithtextidevice import FlashWithTextIdevice
        from exe.engine.externalurlidevice import ExternalUrlIdevice
        from exe.engine.imagemagnifieridevice import ImageMagnifierIdevice 
        # converting Maths Idevice -> FreeTextIdevice:
        #from exe.engine.mathidevice           import MathIdevice
        from exe.engine.multichoiceidevice import MultichoiceIdevice
        #from exe.engine.rssidevice import RssIdevice
        from exe.engine.multiselectidevice import MultiSelectIdevice
        #from exe.engine.appletidevice import AppletIdevice
        from exe.engine.flashmovieidevice import FlashMovieIdevice
        from exe.engine.quiztestidevice import QuizTestIdevice
        # JR
        # Necesarios para la FPD
        from exe.engine.reflectionfpdidevice import ReflectionfpdIdevice
        from exe.engine.reflectionfpdmodifidevice import ReflectionfpdmodifIdevice
        from exe.engine.clozefpdidevice import ClozefpdIdevice
        from exe.engine.clozelangfpdidevice import ClozelangfpdIdevice
        from exe.engine.parasabermasfpdidevice import ParasabermasfpdIdevice
        from exe.engine.debesconocerfpdidevice import DebesconocerfpdIdevice
        from exe.engine.citasparapensarfpdidevice import CitasparapensarfpdIdevice
        from exe.engine.recomendacionfpdidevice import RecomendacionfpdIdevice
        from exe.engine.verdaderofalsofpdidevice import VerdaderofalsofpdIdevice
        from exe.engine.seleccionmultiplefpdidevice import SeleccionmultiplefpdIdevice
        from exe.engine.eleccionmultiplefpdidevice import EleccionmultiplefpdIdevice
        from exe.engine.casopracticofpdidevice import CasopracticofpdIdevice
        from exe.engine.ejercicioresueltofpdidevice import EjercicioresueltofpdIdevice
        from exe.engine.destacadofpdidevice import DestacadofpdIdevice 
        #from exe.engine.correccionfpdidevice		import CorreccionfpdIdevice
        from exe.engine.orientacionesalumnadofpdidevice import OrientacionesalumnadofpdIdevice
        from exe.engine.orientacionestutoriafpdidevice import OrientacionestutoriafpdIdevice
        from exe.engine.freetextfpdidevice import FreeTextfpdIdevice
        
        # eXelearningPlus iDevices
        from exe.engine.scormclozeidevice import ScormClozeIdevice
        from exe.engine.scormmultiselectidevice import ScormMultiSelectIdevice
        from exe.engine.scormdropdownidevice import ScormDropDownIdevice
        from exe.engine.scormmulticlozeidevice import ScormMultiClozeIdevice
        from exe.engine.opinionidevice        import OpinionIdevice
        from exe.engine.dropdownidevice import DropDownIdevice
        from exe.engine.scormmultiselectindfeedbackidevice import ScormMultiSelectIndFeedbackIdevice

        factoryExtendedIdevices = []
        
        factoryExtendedIdevices.append(FreeTextIdevice())
        factoryExtendedIdevices.append(MultichoiceIdevice())
        factoryExtendedIdevices.append(ReflectionIdevice())
        factoryExtendedIdevices.append(CasestudyIdevice())
        factoryExtendedIdevices.append(TrueFalseIdevice())
        defaultImage = unicode(self.config.webDir / "images" / "sunflowers.jpg")
        # converting ImageWithTextIdevice -> FreeTextIdevice:
        #factoryExtendedIdevices.append(ImageWithTextIdevice(defaultImage))
        factoryExtendedIdevices.append(ImageMagnifierIdevice(defaultImage))
        defaultImage = unicode(self.config.webDir / "images" / "sunflowers.jpg")
        #defaultSite = 'http://%s.wikipedia.org/' % self.config.locale
        #factoryExtendedIdevices.append(WikipediaIdevice(defaultSite))
        #JR: Eliminamos este iDevices de los extendidos
        #factoryExtendedIdevices.append(AttachmentIdevice())
        factoryExtendedIdevices.append(GalleryIdevice())
        factoryExtendedIdevices.append(ClozeIdevice())
        #factoryExtendedIdevices.append(ClozelangIdevice())
        #JR: Eliminamos este iDevices de los extendidos
        #factoryExtendedIdevices.append(FlashWithTextIdevice())
        factoryExtendedIdevices.append(ExternalUrlIdevice()) 
        # converting Maths Idevice -> FreeTextIdevice:
        #factoryExtendedIdevices.append(MathIdevice())
        #JR: Eliminamos este iDevices de los extendidos
        #factoryExtendedIdevices.append(MultimediaIdevice())
        #factoryExtendedIdevices.append(RssIdevice())
        factoryExtendedIdevices.append(MultiSelectIdevice())
        #factoryExtendedIdevices.append(AppletIdevice())
        #JR: Eliminamos este iDevices de los extendidos
        #factoryExtendedIdevices.append(FlashMovieIdevice())
        #modification lernmodule.net
        #factoryExtendedIdevices.append(QuizTestIdevice())
        #end modification lernmodule.net
        # JR
        # iDevices para la FPD
        factoryExtendedIdevices.append(ReflectionfpdIdevice())
        factoryExtendedIdevices.append(ReflectionfpdmodifIdevice())
        factoryExtendedIdevices.append(ClozefpdIdevice())
        factoryExtendedIdevices.append(ClozelangfpdIdevice())
        factoryExtendedIdevices.append(ParasabermasfpdIdevice())
        factoryExtendedIdevices.append(DebesconocerfpdIdevice())
        factoryExtendedIdevices.append(CitasparapensarfpdIdevice())
        factoryExtendedIdevices.append(RecomendacionfpdIdevice())
        factoryExtendedIdevices.append(VerdaderofalsofpdIdevice())
        factoryExtendedIdevices.append(SeleccionmultiplefpdIdevice())
        factoryExtendedIdevices.append(EleccionmultiplefpdIdevice())
        factoryExtendedIdevices.append(CasopracticofpdIdevice())
        factoryExtendedIdevices.append(EjercicioresueltofpdIdevice())
        factoryExtendedIdevices.append(DestacadofpdIdevice()) 
        #factoryExtendedIdevices.append(CorreccionfpdIdevice())
        factoryExtendedIdevices.append(OrientacionesalumnadofpdIdevice())
        factoryExtendedIdevices.append(OrientacionestutoriafpdIdevice())
        factoryExtendedIdevices.append(FreeTextfpdIdevice())

        # eXelearningPlus
        factoryExtendedIdevices.append(ScormClozeIdevice())
        factoryExtendedIdevices.append(ScormMultiSelectIdevice())
        factoryExtendedIdevices.append(ScormDropDownIdevice())
        factoryExtendedIdevices.append(ScormMultiClozeIdevice())
        factoryExtendedIdevices.append(OpinionIdevice())
        factoryExtendedIdevices.append(DropDownIdevice())
        factoryExtendedIdevices.append(ScormMultiSelectIndFeedbackIdevice())
        
        return factoryExtendedIdevices

        
    def __loadExtended(self):
        """
        Load the Extended iDevices (iDevices coded in Python)
        JR: Modifico esta funcion para que tambien cargue los idevices extendidos de fabrica
        """
        self.__loadUserExtended()

        #JR: Si existe el archivo extended.data cargamos de ahi los iDevices extendidos
        extendedPath = self.config.configDir/'idevices'/'extended.data'
        log.debug("load extended iDevices from "+extendedPath)

        self.factoryiDevices = self.__getFactoryExtendediDevices()

        if extendedPath.exists():
            self.extended = persist.decodeObject(extendedPath.bytes())
        else:
            self.extended = copy.deepcopy(self.factoryiDevices)
            #self.extended = self.factoryiDevices
            for idevice in self.__getIdevicesFPD():
                self.delIdevice(idevice)




        # generate new ids for these iDevices, to avoid any clashes
        for idevice in self.extended:
            idevice.id = self.getNewIdeviceId()
  

    def __loadUserExtended(self):
        """
        Load the user-created extended iDevices which are in the idevices
        directory
        """
        idevicePath = self.config.configDir/'idevices'
        log.debug("load extended iDevices from "+idevicePath)
            
        if not idevicePath.exists():
            idevicePath.makedirs()
        sys.path = [idevicePath] + sys.path
        
        # Add to the list of extended idevices
        for path in idevicePath.listdir("*idevice.py"):
            log.debug("loading "+path)
            moduleName = path.basename().splitext()[0]
            module = __import__(moduleName, globals(), locals(), [])
            module.register(self)

        # Register the blocks for rendering the idevices
        for path in idevicePath.listdir("*block.py"):
            log.debug("loading "+path)
            moduleName = path.basename().splitext()[0]
            module = __import__(moduleName, globals(), locals(), [])
            module.register()


    def __loadGeneric(self):
        """
        Load the Generic iDevices from the appdata directory
        """
        genericPath = self.config.configDir/'idevices'/'generic.data'
        log.debug("load generic iDevices from "+genericPath)
        if genericPath.exists():
            self.generic = persist.decodeObject(genericPath.bytes())
            self.__upgradeGeneric()
            self.factoryiDevices += self.__createGeneric()
        else:
            self.generic = self.__createGeneric()
            self.factoryiDevices += self.generic


        # generate new ids for these iDevices, to avoid any clashes
        for idevice in self.generic:
            idevice.id = self.getNewIdeviceId()

    def __upgradeGeneric(self):
        """
        Upgrades/removes obsolete generic idevices from before
        """
        # We may have two reading activites,
        # one problably has the wrong title, 
        # the other is redundant
        readingActivitiesFound = 0
        for idevice in self.generic:
            if idevice.class_ == 'reading':
                if readingActivitiesFound == 0:
                    # Rename the first one we find
                    idevice.title = x_(u"Reading Activity")
                    # and also upgrade its feedback field from using a simple
                    # string, to a subclass of TextAreaField.
                    # While this will have been initially handled by the
                    # field itself, and if not, then by the genericidevice's
                    # upgrade path, this is included here as a possibly
                    # painfully redundant safety check due to the extra
                    # special handing of generic idevices w/ generic.dat
                    for field in idevice.fields:
                        if isinstance(field, FeedbackField):
                            # must check for the upgrade manually, since
                            # persistence versions not used here.
                            # (but note that the persistence versioning
                            #  will probably have ALREADY happened anyway!)
                            if not hasattr(field,"content"): 
                                # this FeedbackField has NOT been upgraded:
                                field.content = field.feedback 
                                field.content_w_resourcePaths = field.content
                                field.content_wo_resourcePaths = field.content
                else:
                    # Destroy the second
                    self.generic.remove(idevice)
                readingActivitiesFound += 1
                if readingActivitiesFound == 2:
                    break
        self.save()

    def __createGeneric(self):
        """
        Create the Generic iDevices which you get for free
        (not created using the iDevice editor, but could have been)
        Called when we can't find 'generic.data', generates an initial set of 
        free/builtin idevices and writes the new 'generic.data' file
        JR: Modifico este metodo para que acepte otro parametro que sera la lista 
        en la que anadimos los idevices gnericos
        """
        
        idevices = []

        from exe.engine.genericidevice import GenericIdevice

        readingAct = GenericIdevice(_(u"Reading Activity"), 
                                    u"reading",
                                    _(u"University of Auckland"), 
                                    x_(u"""<p>The Reading Activity will primarily 
be used to check a learner's comprehension of a given text. This can be done 
by asking the learner to reflect on the reading and respond to questions about 
the reading, or by having them complete some other possibly more physical task 
based on the reading.</p>"""),
                                    x_(u"<p>Teachers should keep the following "
                                        "in mind when using this iDevice: </p>"
                                        "<ol>"
                                        "<li>"
                                        "Think about the number of "
                                        "different types of activity "
                                        "planned for your resource that "
                                        "will be visually signalled in the "
                                        "content. Avoid using too many "
                                        "different types or classification "
                                        "of activities otherwise learner "
                                        "may become confused. Usually three "
                                        "or four different types are more "
                                        "than adequate for a teaching "
                                        "resource."
                                        "</li>"
                                        "<li>"
                                        "From a visual design "
                                        "perspective, avoid having two "
                                        "iDevices immediately following "
                                        "each other without any text in "
                                        "between. If this is required, "
                                        "rather collapse two questions or "
                                        "events into one iDevice. "
                                        "</li>"
                                        "<li>"
                                        "Think "
                                        "about activities where the "
                                        "perceived benefit of doing the "
                                        "activity outweighs the time and "
                                        "effort it will take to complete "
                                        "the activity. "
                                        "</li>"
                                        "</ol>")) 
        readingAct.emphasis = Idevice.SomeEmphasis
        readingAct.addField(TextAreaField(_(u"What to read"), 
_(u"""Enter the details of the reading including reference details. The 
referencing style used will depend on the preference of your faculty or 
department.""")))
        readingAct.addField(TextAreaField(_(u"Activity"), 
_(u"""Describe the tasks related to the reading learners should undertake. 
This helps demonstrate relevance for learners.""")))

        readingAct.addField(FeedbackField(_(u"Feedback"), 
_(u"""Use feedback to provide a summary of the points covered in the reading, 
or as a starting point for further analysis of the reading by posing a question 
or providing a statement to begin a debate.""")))

        #idevices.append(readingAct)
    
        objectives = GenericIdevice(_(u"Objectives"), 
                                    u"objectives",
                                    _(u"University of Auckland"), 
_(u"""Objectives describe the expected outcomes of the learning and should
define what the learners will be able to do when they have completed the
learning tasks."""), 
                                    u"")
        objectives.emphasis = Idevice.SomeEmphasis

        objectives.addField(TextAreaField(_(u"Objectives"),
_(u"""Type the learning objectives for this resource.""")))
        #idevices.append(objectives)
        #added kthamm summary idevice 111027
        devsummary = GenericIdevice(_(u"Summary"), 
                                    u"devsummary",
                                    _(u"University of Auckland"), 
_(u"""Provide a summary of the learning resource."""), 
                                    u"")
        devsummary.emphasis = Idevice.SomeEmphasis

        devsummary.addField(TextAreaField(_(u"Summary"),
_(u"""Type a brief summary for this resource.""")))
        idevices.append(devsummary)
        #end added

        #added kthamm preview idevice 111028 
        devpreview = GenericIdevice(_(u"Preview"), 
                                    u"devpreview",
                                    _(u"University of Auckland"), 
_(u"""A preview to introduce the learning resource"""), 
                                    u"")
        devpreview.emphasis = Idevice.SomeEmphasis

        devpreview.addField(TextAreaField(_(u"Preview"),
_(u"""Type the learning objectives for this resource.""")))
        idevices.append(devpreview)
        #end added

        #added kthamm 111028 resource idevice
        devresource = GenericIdevice(_(u"Resource"), 
                                    u"devresource",
                                    _(u"University of Auckland"), 
                                    x_(u""" """),
                                    x_(u" ")) 
        devresource.emphasis = Idevice.SomeEmphasis
        devresource.addField(TextAreaField(_(u"Resource"), 
_(u"""Enter an URL to a resource, you want to provide. Mark the URL and click on the link button in the editor""")))
#        devresource.addField(TextAreaField(_(u"Activity"), 
#_(u"""Describe the tasks related to the reading learners should undertake. 
#This helps demonstrate relevance for learners.""")))
#
#        devresource.addField(FeedbackField(_(u"Feedback"), 
#_(u"""Use feedback to provide a summary of the points covered in the reading, 
#or as a starting point for further analysis of the reading by posing a question 
#or providing a statement to begin a debate.""")))

        idevices.append(devresource)
        #end added
 

        #added kthamm 111028 discussion idevice
        devdiscussion = GenericIdevice(_(u"Discussion"), 
                                    u"devdiscussion",
                                    _(u"University of Auckland"), 
                                    x_(u""" """),
                                    x_(u" ")) 
        devdiscussion.emphasis = Idevice.SomeEmphasis
        devdiscussion.addField(TextAreaField(_(u"Discussion"), 
_(u"""Enter the details of the reading including reference details. The 
referencing style used will depend on the preference of your faculty or 
department.""")))
        devdiscussion.addField(TextAreaField(_(u"Activity"), 
_(u"""Describe the tasks related to the reading learners should undertake. 
This helps demonstrate relevance for learners.""")))

        idevices.append(devdiscussion)
        #end added

        preknowledge = GenericIdevice(_(u"Preknowledge"), 
                                      u"preknowledge",
                                      "", 
_(u"""Prerequisite knowledge refers to the knowledge learners should already
have in order to be able to effectively complete the learning. Examples of
pre-knowledge can be: <ul>
<li>        Learners must have level 4 English </li>
<li>        Learners must be able to assemble standard power tools </li></ul>
"""), u"")
        preknowledge.emphasis = Idevice.SomeEmphasis
        preknowledge.addField(TextAreaField(_(u"Preknowledge"), 
_(u"""Describe the prerequisite knowledge learners should have to effectively
complete this learning.""")))
        #idevices.append(preknowledge)
        
        activity = GenericIdevice(_(u"Activity"), 
                                  u"activity",
                                  _(u"University of Auckland"), 
_(u"""An activity can be defined as a task or set of tasks a learner must
complete. Provide a clear statement of the task and consider any conditions
that may help or hinder the learner in the performance of the task."""),
u"")
        activity.emphasis = Idevice.SomeEmphasis
        activity.addField(TextAreaField(_(u"Activity"),
_(u"""Describe the tasks the learners should complete.""")))
        #idevices.append(activity)

        self.save()
        return idevices


    def __createReading011(self):
        """
        Create the Reading Activity 0.11
        We do this only once when the user first runs eXe 0.11
        """
        from exe.engine.genericidevice import GenericIdevice

        readingAct = GenericIdevice(_(u"Reading Activity 0.11"), 
                                    u"reading",
                                    _(u"University of Auckland"), 
                                    x_(u"""<p>The reading activity, as the name 
suggests, should ask the learner to perform some form of activity. This activity 
should be directly related to the text the learner has been asked to read. 
Feedback to the activity where appropriate, can provide the learner with some 
reflective guidance.</p>"""),
                                    x_(u"Teachers should keep the following "
                                        "in mind when using this iDevice: "
                                        "<ol>"
                                        "<li>"
                                        "Think about the number of "
                                        "different types of activity "
                                        "planned for your resource that "
                                        "will be visually signalled in the "
                                        "content. Avoid using too many "
                                        "different types or classification "
                                        "of activities otherwise learner "
                                        "may become confused. Usually three "
                                        "or four different types are more "
                                        "than adequate for a teaching "
                                        "resource."
                                        "</li>"
                                        "<li>"
                                        "From a visual design "
                                        "perspective, avoid having two "
                                        "iDevices immediately following "
                                        "each other without any text in "
                                        "between. If this is required, "
                                        "rather collapse two questions or "
                                        "events into one iDevice. "
                                        "</li>"
                                        "<li>"
                                        "Think "
                                        "about activities where the "
                                        "perceived benefit of doing the "
                                        "activity outweighs the time and "
                                        "effort it will take to complete "
                                        "the activity. "
                                        "</li>"
                                        "</ol>")) 
        readingAct.emphasis = Idevice.SomeEmphasis
        readingAct.addField(TextAreaField(_(u"What to read"), 
_(u"""Enter the details of the reading including reference details. The 
referencing style used will depend on the preference of your faculty or 
department.""")))
        readingAct.addField(TextAreaField(_(u"Activity"), 
_(u"""Describe the tasks related to the reading learners should undertake. 
This helps demonstrate relevance for learners.""")))

        readingAct.addField(FeedbackField(_(u"Feedback"), 
_(u"""Use feedback to provide a summary of the points covered in the reading, 
or as a starting point for further analysis of the reading by posing a question 
or providing a statement to begin a debate.""")))
    
        objectives = GenericIdevice(_(u"Objectives"), 
                                    u"objectives",
                                    _(u"University of Auckland"), 
_(u"""Objectives describe the expected outcomes of the learning and should
define what the learners will be able to do when they have completed the
learning tasks."""), 
                                    u"")
        objectives.emphasis = Idevice.SomeEmphasis

        objectives.addField(TextAreaField(_(u"Objectives"),
_(u"""Type the learning objectives for this resource.""")))
        self.generic.append(objectives)

        preknowledge = GenericIdevice(_(u"Preknowledge"), 
                                      u"preknowledge",
                                      "", 
_(u"""Prerequisite knowledge refers to the knowledge learners should already
have in order to be able to effectively complete the learning. Examples of
pre-knowledge can be: <ul>
<li>        Learners must have level 4 English </li>
<li>        Learners must be able to assemble standard power tools </li></ul>
"""), u"")
        preknowledge.emphasis = Idevice.SomeEmphasis
        preknowledge.addField(TextAreaField(_(u"Preknowledge"), 
_(u"""Describe the prerequisite knowledge learners should have to effectively
complete this learning.""")))
        self.generic.append(preknowledge)
        
        activity = GenericIdevice(_(u"Activity"), 
                                  u"activity",
                                  _(u"University of Auckland"), 
_(u"""An activity can be defined as a task or set of tasks a learner must
complete. Provide a clear statement of the task and consider any conditions
that may help or hinder the learner in the performance of the task."""),
u"")
        activity.emphasis = Idevice.SomeEmphasis
        activity.addField(TextAreaField(_(u"Activity"),
_(u"""Describe the tasks the learners should complete.""")))
        self.generic.append(activity)

        self.save()


    def save(self):
        """
        Save the Generic iDevices to the appdata directory
        """
        idevicesDir = self.config.configDir/'idevices'
        if not idevicesDir.exists():
            idevicesDir.mkdir()
        fileOut = open(idevicesDir/'generic.data', 'wb')
        fileOut.write(persist.encodeObject(self.generic))
        #JR: Guardamos tambien los iDevices extendidos
        fileOut = open(idevicesDir/'extended.data', 'wb')
        fileOut.write(persist.encodeObject(self.extended))

# ===========================================================================
