from time import sleep
import select
import sys
from queue import Queue, Empty
import subprocess
from ipaddress import ip_address
import re
import shlex
from collections import namedtuple
import os
from threading import Thread
from tool import tools
from module import modules


Result = namedtuple('Result', ['target', 'cmd', 'output'])
the_prompt = "> "   

def prompt():
    sys.stdout.write(the_prompt)
    sys.stdout.flush()

def banner():
    
    print(r"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~     __  ___                   ______               __ ~
~    /  |/  /_____ _____ _   __/_  __/____   ____   / / ~
~   / /|_/ // ___// ___/| | / / / /  / __ \ / __ \ / /  ~
~  / /  / /(__  )(__  ) | |/ / / /  / /_/ // /_/ // /   ~
~ /_/  /_//____//____/  |___/ /_/   \____/ \____//_/    ~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
""")


class Target:
    ip = None
    domain_name = None
    ports = set()
    files = set()
    save_prefix = ""

    def __init__(self, **kwargs):
        self.ip = kwargs.get('ip', None)
        self.domain_name = kwargs.get('domain_name', None)
        assert(self.ip or self.domain_name)
        self.save_prefix = self.domain_name if self.domain_name else self.ip
        self.save_prefix = self.save_prefix.replace(".", "-")

class AutoScanner:


    def __init__(self):
        self.cmd_qq = Queue()
        self.msg_qq = Queue()
        self.engagement_name = ""
        self.cli_results = []
        self.targets = [] # { ip: ip, domain_name: "", ports: set(), files: [] }
        self.targets_file = ""
#        self.keywords? usernames? emails? passwords?

### OPTIONS
        self.quiet = False
        self.threading = True
        self.is_save_to_file = True
        self.save_prefix = ""
### fire up the cmd queue
        cmd_qq_thread = Thread(target=self.consume_cmd_qq, daemon=True).start()


    def consume_cmd_qq(self):
        while True:
            ready_cmd = self.cmd_qq.get()
            self.run_cli_cmd(ready_cmd)


    def thread_cmd(self, ready_cmd):
        if self.threading:
            th = Thread(target=self.run_cli_cmd, args=[ready_cmd])
            th.start()
        else:
            self.run_cli_cmd(ready_cmd)


    def run_cli_cmd(self, ready_cmd):
        tool, target, cmd = ready_cmd
        cmd_str = ' '.join(cmd)
        self.msg_qq.put(f"Running: {cmd_str}")
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True)
        except Exception as e:
            self.msg_qq.put(f"Command failed: {e}")
            return

        output = proc.stdout
        tools[tool].process_result(target, output)
        if self.is_save_to_file:
            output_file = f"{self.save_prefix}{target.save_prefix}_{tool}"
            if not self.quiet:
                self.msg_qq.put(f"Finished: {cmd_str} -> written to: {output_file}")
            target.files.add(output_file)
            with open(output_file, 'a') as f:
                f.write("\nCommand ran: " + " ".join(cmd) + "\n")
                f.write(output)
                
            


    def list_tools(self):
        for name, tool in tools.items():
            print(f"{name}: {tool.description}")
            print(f"    {tool.default_cmd}")


    def process(self, cmd):
        if len(cmd.strip()) == 0:
            # this should display number of jobs / which modules/tools are still running
            return

        # this sort of thing gets messy / turns into an abstract syntax tree quick,
        # so maybe we think ahead about that, but for now it's very simple.
        cmd, *args = shlex.split(cmd)
        if cmd == 'quit' or cmd == 'q':
            exit(0)
        elif cmd in modules:
            mod = modules[cmd]
            self.msg_qq.put(f"Adding {mod.name} module to queue...")
            for ready_cmd in mod.run(self.targets):
                self.cmd_qq.put(ready_cmd)
        elif cmd in tools:
            tool = tools[cmd]
            if len(args) == 0 or args[0].lower() == 'help':
                tool.list_cmds()
            else:
                tool_cmd = args[0]
                if tool_cmd in tool.cmds:
                    self.msg_qq.put(f"Adding {tool.name} - {tool_cmd} to queue...")
                    for ready_cmd in tool.for_each(self.targets, *args):
                        self.cmd_qq.put(ready_cmd)
                else:
                    print(f"Unknown command for {tool.name}: {tool_cmd}")

    def startup(self):
        name = ""
        while len(name) < 1 or len(name) > 128 or not re.fullmatch(r"[0-9a-zA-Z_\-]+", name):
            name = input("Engagement name: ")

        self.engagement_name = name

        save_dir = ""
        while not os.path.exists(save_dir):
            if len(save_dir):
                print("Must be valid path")

            save_dir = input("Output dir (leave blank for cwd): ")
            if not save_dir.startswith('/') and not save_dir.startswith('.'):
                save_dir = './' + save_dir
            if save_dir[-1] != '/':
                save_dir += '/'
        self.save_prefix = save_dir + name + '/'
        if os.path.exists(self.save_prefix):
            if input("Engagement already exists. Continue? y/n: ").lower() == 'n':
                exit(0)
            # TODO: else use settings from existing engagment
        else:
            os.mkdir(self.save_prefix)

        targets_file = ""
        while not os.path.exists(targets_file):
            targets_file = input("Path to targets file: ")

        self.targets_file = targets_file
        with open(targets_file) as f:
            for line in f.readlines():
                line = line.strip()
                try:
                    ip_address(line)
                    self.targets.append(Target(ip=line))
                except:
                    self.targets.append(Target(domain_name=line.strip()))


    def run(self):
        prompt()

        while True:
            if not self.msg_qq.empty():
                print()
                while not self.msg_qq.empty():
                    print(self.msg_qq.get())
                    sleep(.1)
                prompt()

            ready, _, _ = select.select([sys.stdin], [], [], 1)
            if ready:

                line = sys.stdin.readline().strip()
                self.process(line)
                prompt()

            sleep(.1)



    # TODO: add_target, remove_target, add_target_port, remove_target_port, uh and a ton of other stuff

if __name__ == "__main__":
    banner()
    scanner = AutoScanner()
    # TODO: argparse and use cli inputs or startup()

    scanner.startup()
    for target in scanner.targets:
        target.ports.add(80)
        target.ports.add(443)
    scanner.run()


        

