import os
import signal
import subprocess
import threading
import time

from smiler.instrumenting.general_exceptions import MsgException


TIMEOUT_ERROR_VALUE = 1111

def runOnce(cmd, timeout_time=None, return_output=True, stdin_input=None):
    """Spawns a subprocess to run the given shell command.

    Args:
        cmd: shell command to run
        timeout_time: time in seconds to wait for command to run before aborting.
        return_output: if True return output of command as string. Otherwise,
            direct output of command to stdout.
        stdin_input: data to feed to stdin
    Returns:
        output of command
    """

    start_time = time.time()
    so = []
    pid = []
    return_code = [] # hack to store results from a nested function
    
    def Run():
        if return_output:
            output_dest = subprocess.PIPE
        else:
            # None means direct to stdout
            output_dest = None
        if stdin_input:
            stdin_dest = subprocess.PIPE
        else:
            stdin_dest = None
        
        pipe = subprocess.Popen(
                cmd,
                #executable='/bin/bash',
                stdin=stdin_dest,
                stdout=output_dest,
                stderr=subprocess.PIPE,
                shell=True)
        pid.append(pipe.pid)
        try:
            output, err = pipe.communicate()
            if err:
                print err
            if output is not None and len(output) > 0:
                so.append(output)
        except OSError, e:
            so.append("ERROR: OSError!")
        return_code.append(pipe.returncode)
    
    t = threading.Thread(target=Run)
    t.start()
    
    break_loop = False
    while not break_loop:
        if not t.isAlive():
            break_loop = True

        # Check the timeout
        if (not break_loop and timeout_time is not None
                and time.time() > start_time + timeout_time):
            try:
                os.kill(pid[0], signal.SIGKILL)
            except OSError:
                # process already dead. No action required.
                pass
            so.append("ERROR: Timeout!")
            return_code[0] = TIMEOUT_ERROR_VALUE
        if not break_loop:
            time.sleep(0.1)

    t.join()
    output = "".join(so)
    
    return (return_code[0], output)


#Exceptions
class TimeoutException(MsgException):
    '''
    Timeout exception.
    '''
