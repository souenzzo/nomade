#!/usr/bin/env python3

from nomade import ssh, cat


task = ssh({ "target": "zervidor"
           , "task": cat({ "name": "/etc/hostname" })})

res = task.run()

print(res)
