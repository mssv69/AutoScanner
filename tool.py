import re
from collections import namedtuple
from enum import Enum
from enum import auto
from abc import ABC
from config import CONFIG

class ToolType(Enum):
    NONE = auto()
    PORTSCAN = auto()
    WEB = auto()
    SUBDOMAIN = auto()


Command = namedtuple("Command", ["name", "desc", "get_cmd"])
ReadyCmd = namedtuple("ReadyCmd", ["tool", "target", "cmd"])

class CliTool(ABC):
    name = "Name"
    tool_type = ToolType.NONE # tags instead maybe?
    description = "Description"
    cmds = dict() # map of name_for_cmd: function that returns a command (list) ready for subprocess

    def process_result(self, target, output):
        pass

    def list_cmds(self):
        for cmd in self.cmds.values():
            print(cmd.name)
            print("    " + cmd.desc)

    def for_each(self, targets, *args): # Override this
        """ returns (target, [...subprocess ready cmd ]) """
        assert(args[0] in self.cmds)
        cmd_name = args[0]
        for target in targets:
            target_str = target.ip if target.ip else target.domain_name
            yield (target, self.cmds[cmd_name].get_cmd(target_str))




class Nikto(CliTool):
    name = "nikto"
    tool_type = ToolType.WEB
    description = "Automated web enumeration tool"
    
    def __init__(self):
        self.cmds = {
                "default": Command("default",
                                   f"{self.name} -h <url>",
                                   lambda url: [ self.name, "-h", url ])
                }

    def for_each(self, targets, *args):
        assert(args[0] in self.cmds)
        cmd_name = args[0]
        for target in targets:
            target_str = target.ip if target.ip else target.domain_name
            for port in target.ports & CONFIG["web_ports"]:
                yield ReadyCmd(self.name, target, self.cmds[cmd_name].get_cmd(f"{target_str}:{port}"))



    def process_result(self, target, output):
        pass



class Nmap(CliTool):
    name = "nmap"
    tool_type = ToolType.PORTSCAN
    desciption = "It's the portscanner"

    def __init__(self):
        self.cmds = {
                "tcp_fast": Command("tcp_fast",
                                    f"sudo {self.name} -p- -T4 --open <ip>",
                                    lambda ip: ['sudo', self.name, '-p-', '-T4', ip ]
                ),
                "tcp": Command(
                        "tcp",
                        f"sudo {self.name} -p- -Pn --open -vvv <ip>",
                        lambda ip: ['sudo', self.name, '-p-', '-Pn', '--open', '-vvv', ip ]
                    )
                }

    def process_result(self, target, output):
        pass
#        ports = re.findall(f"(\d+)/open", output)
#        print(ports)


    def for_each(self, targets, *args):
        assert(args[0] in self.cmds)
        cmd_name = args[0]
        for target in targets:
            if target.ip:
                yield ReadyCmd(self.name, target, self.cmds[cmd_name].get_cmd(target.ip))

        



tools = {
            Nikto.name: Nikto(),
            Nmap.name: Nmap()
        }
