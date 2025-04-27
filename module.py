from abc import ABC
from config import CONFIG
from tool import tools


class MssvModule(ABC):
    name = "Default name"
    description = "Default description"
    tool_list = [
                (tools["nikto"], "default")
            ]

    def help(self):
        # TODO
        pass

    def run(self, targets):
        for tool, scan_type in self.tool_list:
            for rdy_cmd in tool.for_each(targets, scan_type):
                yield rdy_cmd


class EnumModule(MssvModule):
    name = "enumerate"
    description = \
"""Basic enumeration module:
    nmap tcp
    nmap service
    nmap udp
    nikto"""

    tool_list = [
                (tools["nmap"], "tcp_fast"),
                (tools["nikto"], "default"),
            ]

        
modules = {
        EnumModule.name: EnumModule()
    }
