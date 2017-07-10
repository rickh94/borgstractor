#!/usr/bin/env python3
# borg_command.py - generates calls to borg programatically instead of
# manually

import config
import subprocess
import os
import sys
import atexit
import settings


# borg_command() - generates borg calls
# mandatory arguments:
#   runtype: either run or popen depending on need
#   subcommand: list, mount, umount, extract
# other arguments:
#   list: (optional) arg[0] can be the name of a specific backup to list files in that backup
#   mount: (mandatory) arg[0] must be the name of a specific backup to mount
#   extract: (mandatory) arg[0] must be the backup to extract from, arg[1]
#   must be the file path to extract.
def create(
        runtype,
        subcommand, 
        *args
        ):
    # add command and subcommand
    full_command = ['borg']
    full_command.append(subcommand)
    # handle options differently based on subcommand
    if subcommand == 'list':
        # add repopath
        tmp = getattr(settings, 'repopath')
        # add folder path if it exists
        # append backup name if provided
        try:
            tmp2 = args[0]
            tmp = tmp + '::' + tmp2
        except IndexError:
            pass
        # append constructed command
        full_command.append(tmp)
    elif subcommand == 'mount':
        full_command.append(getattr(settings, 'repopath') + '::' + args[0])
        full_command.append(getattr(settings, 'mountpoint'))
        atexit.register(create, 'run', 'umount')
        # it may raise IndexError but this can only be raised by a bug anyway.
    elif subcommand == 'umount':
        full_command.append(getattr(settings, 'mountpoint'))
    elif subcommand == 'extract':
        # add backup to extract from
        full_command.append(getattr(settings, 'repopath') + '::' + args[0])
        # add file to extract
        full_command.append(args[1])
    
    # return based on runtype option
    if runtype == 'Popen' or runtype == 'popen':
        return subprocess.Popen( \
                full_command, \
                stdout=subprocess.PIPE, \
                stderr=subprocess.STDOUT, \
                env=dict(os.environ, BORG_PASSPHRASE=getattr(settings, 'passphrase'))
                )
    elif runtype == 'run':
        return subprocess.run( \
                full_command, \
                stdout=subprocess.PIPE, \
                stderr=subprocess.STDOUT, \
                env=dict(os.environ, BORG_PASSPHRASE=getattr(settings, 'passphrase'))
                )
    else:
        raise SyntaxError("no valid runtype found")

# TESTS
# run = borg_command('Popen', 'list')
# ret = run.communicate()[0].decode(sys.stdout.encoding),run.returncode
# print(ret[0])
#
# backup = input("paste in the backup name")
# print(backup)
# run2 = borg_command('Popen', 'mount', backup)
# ret2 = run2.communicate()[0].decode(sys.stdout.encoding),run.returncode
#
# input('press enter to continue')
# borg_command('run', 'umount')
#
# run3 = borg_command('Popen', 'list', backup)
# ret3 = run3.communicate()[0].decode(sys.stdout.encoding),run.returncode
# print(ret3[0])
#
# filename = input('paste filename')
# os.chdir(getattr(settings, 'extractdir'))
# run4 = borg_command('run', 'extract', backup, filename)
# print('press enter to continue')
#
