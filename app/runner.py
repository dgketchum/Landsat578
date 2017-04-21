# ===============================================================================
# Copyright 2017 dgketchum
# Adapted from Jake Ross, https://github.com/jirhiker
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================

import sys
import os
pp = os.path.realpath(__file__)
sys.path.append(os.path.dirname(os.path.dirname(pp)))

from app.paths import paths
from config import Config, check_config

CLI_ENABLED = False


def run_model():
    print 'Running Downloader'
    cfg = Config()
    for runspec in cfg.runspecs:
        paths.build(runspec.input_root, runspec.output_root)

        etrm = Processes(runspec)
        etrm.configure_run(runspec)
        etrm.run()


def run_help():
    print 'help'


def run_commands():
    keys = ('model', 'rew', 'help')
    print 'Available Commands: {}'.format(','.join(keys))


def welcome():
    print '''====================================================================================

Available commands are enumerated using "commands"
For more information regarding a specific command use "help <command>". Replace <command> with the command of interest

'''


def run():
    # check for a configuration file
    check_config()

    cmds = {'model': run_model}

    welcome()

    if CLI_ENABLED:
        while 1:
            cmd = raw_input('>>> ')
            try:
                func = cmds[cmd]
            except KeyError:
                continue

            func()
    else:
        run_model()


if __name__ == '__main__':
    run()

# ===============================================================================
