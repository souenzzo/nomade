#!/usr/bin/env python


class nomade:
    def __init__(self, state = {}):
        self.state = state
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
    def run(self):
        from subprocess import run
        from pickle import dump, load
        target = self.state["target"]
        task = self.state["task"]
        with open("./task.pyc", "bw") as f:
            dump(task, f)
        rsync = ["rsync", "-a", "--delete", "../nomade", "%s:"%(target)]
        run(rsync)

        ssh = ["ssh", "%s"%(target), "cd nomade && python3 -m nomade task.pyc state.pyc"]
        run(ssh)

        rsync = ["rsync", "-a", "--delete", "%s:nomade/state.pyc"%(target), "."]
        run(rsync)

        with open('./state.pyc', 'br') as f:
            res = load(f)
        return { "status": "ok", "task": res }


if __name__ == "__main__":
    from sys import argv
    from pickle import dump, load
    with open(argv[1], 'br') as f:
        task = load(f)
    res = task.run()
    with open(argv[2], 'bw') as f:
        dump(res, f)


