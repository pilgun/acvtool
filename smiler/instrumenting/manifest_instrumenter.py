import os

from smiler.config import config
from general_exceptions import MsgException
from android_manifest import AndroidManifest, \
    ManifestAlreadyInstrumentedException
import shutil


def instrumentAndroidManifestFile(pathToUnmodifiedFile, pathToModifiedFile=None, addSdCardPermission=True):
        '''
        Adds instrumentation tag with predefined attributes corresponding to our
        instrumentation classes to the provided manifest file. If 
        instrumentation tag exists, this method substitutes it with appropriate
        one. Adds (if necessary) to the provided AndroidManifest file permission
        to write to the external storage.
        
        Args:
            :param pathToUnmodifiedFile: path to the unmodified 
                AndroidManifest.xml file
            :param pathToModifiedFile: path where to store modified
                AndroidManifest.xml file. If pathToModifiedFile==None, the 
                initial pathToUnmodifiedFile will be overridden.
        '''
        if not os.path.isfile(pathToUnmodifiedFile):
            raise IllegalArgumentException("File [%s] does not exist!" % pathToUnmodifiedFile) 
        androidManifest = AndroidManifest(pathAndroidManifest=pathToUnmodifiedFile)
        packageName = androidManifest.getPackageName()
        try:
            androidManifest.addInstrumentation(config.INSTRUMENTING_NAME, packageName)
        except ManifestAlreadyInstrumentedException:
            androidManifest.removeExistingInstrumentation() 
            androidManifest.addInstrumentation(config.INSTRUMENTING_NAME, packageName)
        
        if addSdCardPermission:
            androidManifest.addUsesPermission("android.permission.WRITE_EXTERNAL_STORAGE")
        
        if not pathToModifiedFile or (pathToUnmodifiedFile == pathToModifiedFile):
            androidManifest.exportManifest(path=None)
        else: 
            androidManifest.exportManifest(path=pathToModifiedFile)
        
class IllegalArgumentException(MsgException):
    '''
    Incorrect parameter argument.
    '''
