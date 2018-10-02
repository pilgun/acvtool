import os
import commander


class ApktoolInterface:
    def __init__(self, javaPath = "java", javaOpts = "-Xms512m -Xmx1024m", pathApktool=os.path.join('libs'), jarApktool="apktool.jar"):
        self.javaPath = javaPath
        self.javaOpts = javaOpts
        self.pathApktool = pathApktool
        self.jarApktool = jarApktool
        #TODO: later we can join path and jar and check if they exist or not
        # if not - generate an exception
    
    def _previewApktoolCommand(self, cmdStr, quiet):
        path = os.path.join(self.pathApktool, self.jarApktool)
        verbose = None
        if quiet:
            verbose = "--quiet"
        else:
            verbose = "--verbose"
            
        apktoolCmd = "%s %s %s" % (path, verbose, cmdStr)
        return apktoolCmd
    
    def _runApktoolCommand(self, commandString):
        cmd = "%s %s -jar %s" % (self.javaPath, self.javaOpts, commandString)
        return commander.runOnce(cmd)

    def _interpResultsDecodeCmd(self, returnCode, cmdOutput):
        output = "Return code is: [%s].\nCommand output: %s" % (returnCode, cmdOutput)
        #TODO: later we can select different routines to process different errors
        if returnCode:
            return (False, output)
        return (True, output)
    
    
    def decode(self, apkPath, dirToDecompile, quiet=True, noSrc=False, noRes=False, debug=True, noDebugInfo=False, force=True, frameworkTag="", frameworkDir="", keepBrokenRes=True):
        options = "decode"
        if noSrc:
            options += " --no-src"
        if noRes:
            options += " --no-res"
        if debug:
            options += " --debug"
        if noDebugInfo:
            options += " --no-debug-info"
        if force:
            options += " --force"
        if frameworkTag:
            options += " --frame-tag '%s'" % frameworkTag
        if frameworkDir:
            options += " --frame-path '%s'" % frameworkDir  
        if keepBrokenRes:
            options += " --keep-broken-res" 
        
        options = "%s -o %s %s" % (options, dirToDecompile, apkPath)
        cmd = self._previewApktoolCommand(options, quiet)
        (returnCode, cmdOutput) = self._runApktoolCommand(cmd)
        return self._interpResultsDecodeCmd(returnCode, cmdOutput)
    

    def _interpResultsBuildCmd(self, returnCode, outputStr):
        retCode = "Return code is: %s" % returnCode
        #NOTE: later we can select different routines to process different errors
        if returnCode:
            output = "%s\n%s" % (retCode, outputStr)
            return (False, output)
        return (True, None)
    
    
    def build(self, srcPath, finalApk, quiet=True, forceAll=False, debug=True, aaptPath=""):
        options = "build"
        if forceAll:
            options += ' --force-all'
        if debug:
            options += ' --debug'
        if aaptPath:
            options += ' --aapt %s' % aaptPath
        
        options = '%s %s -o %s' % (options, srcPath, finalApk)
        cmd = self._previewApktoolCommand(options, quiet)
        (returnCode, outputStr) = self._runApktoolCommand(cmd)
        return self._interpResultsBuildCmd(returnCode, outputStr)
