#!/usr/bin/env python


class nomade:
    def __init__(self, state = {}):
        self.state = state
    def savedeps(self, prefix = "."):
        pass
    def run(self):
        return {}


class cat(nomade):
    def run(self):
        name = self.state["name"]
        with open(name, "r") as f:
            res = f.readlines()
        return res

class ping(nomade):
    def run(self):
        return self.state

class ssh(nomade):
    def dumpState(self, task, prefix = "."):
        from pickle import dump
        from os import mkdir
        import inspect, nomade, shutil
        task.savedeps(prefix)
        mkdir("%s/state"%(prefix))

        fname = inspect.getsourcefile(nomade)
        shutil.copy2(fname, prefix)
        

        
        
        with open("%s/state/task.pyc"%(prefix), "bw") as f:
            dump(task, f)

    def sendState(self, prefix, target):
        from subprocess import run
        rsync = [ "rsync"
                , "-a"
                , "--delete"
                , "%s/"%(prefix)
                , "%s:%s"%(target, prefix)]
        s = run(rsync)
        if s.returncode != 0:
            raise IOError


    def remoteRun(self, prefix, target):
        from subprocess import run
        ssh = ["ssh", 
            "%s"%(target),
            "cd '%s' && python3 -m nomade ./state/task.pyc ./state/state.pyc"%(prefix)]
        s = run(ssh)
        if s.returncode != 0:
            raise IOError

    def getState(self, prefix, target):
        from subprocess import run
        rsync = ["rsync",
                "-a",
                "--delete",
                "%s:%s/state/state.pyc"%(target,prefix),
                "%s/state"%(prefix)]
        s = run(rsync)
        if s.returncode != 0:
            raise IOError

    def restoreState(self, prefix):
        from pickle import load
        with open('%s/state/state.pyc'%(prefix), 'br') as f:
            res = load(f)
        return res
    
    def run(self):
        from pickle import dump, load
        from tempfile import mkdtemp

        target = self.state["target"]
        task = self.state["task"]

        prefix = mkdtemp()
        self.dumpState(task, prefix)

        self.sendState(prefix, target)
        self.remoteRun(prefix, target)
        self.getState(prefix, target)

        res = self.restoreState(prefix)

        return { "status": "ok", "task": res }


if __name__ == "__main__":
    from sys import argv
    from pickle import dump, load
    with open(argv[1], 'br') as f:
        task = load(f)
    res = task.run()
    with open(argv[2], 'bw') as f:
        dump(res, f)


