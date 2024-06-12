import subprocess

def request_pipe(cmd):
    pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = pipe.communicate()

    res = out
    if not out:
        res = err
    
    if pipe.returncode > 0:
        raise Exception("----------------------------------------------------\n\
Out: {}\nError: {}".format(out.decode(), err.decode()))

    return res.decode()
