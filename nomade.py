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
    def dumpState(self, prefix = "."):
        task.savedeps(prefix)
        mkdir("%s/state"%(prefix))
        with open("%s/state/task.pyc"%(prefix), "bw") as f:
            dump(task, f)

    def sendState(self, prefix, target):
        rsync = ["rsync"
                , "-a"
                , "--delete"
                , "%s"%(prefix)
                , "%s:"%(target)]
        run(rsync)

    def remoteRun(self, prefix, target):
        ssh = ["ssh", "%s"%(target), "cd nomade && python3 -m nomade task.pyc state.pyc"]
        run(ssh)
    def getState(self, prefix, target):
        rsync = ["rsync", "-a", "--delete", "%s:nomade/state.pyc"%(target), "."]
        run(rsync)

    def restoreState(self, prefix):
        with open('./state.pyc', 'br') as f:
            res = load(f)
        return res
    
    def run(self):
        from subprocess import run
        from pickle import dump, load
        from tempfile import mkdtemp
        from os import mkdir

        target = self.state["target"]
        task = self.state["task"]

        prefix = mkdtemp()
        self.dumpState(prefix)

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


