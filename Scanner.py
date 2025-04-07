#!/usr/bin/env python3

import subprocess
import re
import os
import sys
import argparse


DEFAULT_WORDLIST = "/usr/share/wordlists/rockyou.txt"
DEFAULT_SUB_WORDLIST = "/usr/share/wordlists/rockyou.txt"
WEB_PORTS = {"80", "443", "8080", "8000", "8443"}

def run_command(command, output_file=None):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    with open(output_file, "w") if output_file else open(os.devnull, "w") as f:
        for line in process.stdout:
            print(line, end="")
            f.write(line)
    process.wait()

def run_nmap(target):
    output_file = f"{target}_openPorts.txt"
    print(f"[*] Running Nmap full scan on {target}...")
    subprocess.run(["sudo", "nmap", "-p-", "-Pn", "--open", "-vvv", "-oG", output_file, target], stdout=subprocess.DEVNULL)
    return output_file

def extract_open_ports(filename):
    with open(filename) as f:
        content = f.read()
    ports = re.findall(r"(\d+)/open", content)
    return ",".join(sorted(set(ports), key=int))

def run_nmap_services(target, ports):
    output_file = f"{target}_sCV_scan.txt"
    print(f"[*] Running Nmap service scan on ports {ports}")
    run_command(["sudo", "nmap", "-p", ports, "-sCV", "-oN", output_file, target])
    return output_file

def detect_web_ports(port_list):
    return [port for port in port_list.split(",") if port in WEB_PORTS]

def run_web_tool(tool, target, port, wordlist):
    url = f"http://{target}:{port}"
    output_file = f"{target}_port{port}_{tool}.txt"
    print(f"[*] Running {tool} on {url}")
    if tool == "nikto":
        cmd = ["nikto", "-h", url]
    elif tool == "dirb":
        cmd = ["dirb", url, wordlist]
    elif tool == "gobuster":
        cmd = ["gobuster", "dir", "-u", url, "-w", wordlist]
    elif tool == "feroxbuster":
        cmd = ["feroxbuster", "-u", url, "-w", wordlist]
    elif tool == "ffuf":
        cmd = ["ffuf", "-u", f"{url}/FUZZ", "-w", wordlist]
    else:
        print(f"[!] Unknown tool: {tool}")
        return
    run_command(cmd, output_file)

def run_subdomain_tool(tool, target, wordlist):
    output_file = f"{target}_subdomains_{tool}.txt"
    print(f"[*] Running {tool} for subdomain enumeration...")
    if tool == "sublist3r":
        cmd = ["sublist3r", "-d", target, "-o", output_file]
    elif tool == "subfinder":
        cmd = ["subfinder", "-d", target, "-o", output_file]
    elif tool == "dnsx":
        cmd = ["dnsx", "-silent", "-d", target, "-w", wordlist]
    elif tool == "ffuf":
        cmd = ["ffuf", "-u", f"https://FUZZ.{target}", "-w", wordlist]
    else:
        print(f"[!] Unknown subdomain tool: {tool}")
        return
    run_command(cmd, output_file)

def generate_html_report(target, files, combined=False):
    html = [f"<html><head><title>{target} Report</title><style>body{{font-family:sans-serif;}} pre{{background:#000;color:#0f0;padding:10px;}}</style></head><body>"]
    html.append(f"<h1>Scan Report: {target}</h1><ul>")
    for file in files:
        section_id = file.replace(".", "_").replace(" ", "_")
        html.append(f'<li><a href="#{section_id}">{file}</a></li>')
    html.append("</ul><hr>")
    for file in files:
        section_id = file.replace(".", "_").replace(" ", "_")
        html.append(f'<h2 id="{section_id}">{file}</h2><pre>')
        try:
            with open(file) as f:
                html.append(f.read())
        except:
            html.append("[!] Failed to read file.")
        html.append("</pre><hr>")
    html.append("</body></html>")
    out_name = "combined_report.html" if combined else f"{target}_report.html"
    with open(out_name, "w") as f:
        f.write("".join(html))
    print(f"[+] HTML report written to {out_name}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", help="IP or domain")
    parser.add_argument("-f", "--file", help="File with multiple targets")
    parser.add_argument("--parallel", action="store_true")
    parser.add_argument("--nmap-only", action="store_true")
    parser.add_argument("--web-only", action="store_true")
    parser.add_argument("--subdomain-only", action="store_true")
    parser.add_argument("--no-nmap", action="store_true")
    parser.add_argument("--tools", help="Comma-separated web tools")
    parser.add_argument("--subtools", help="Comma-separated subdomain tools")
    parser.add_argument("--wordlist", default=DEFAULT_WORDLIST)
    parser.add_argument("--subwordlist", default=DEFAULT_SUB_WORDLIST)
    parser.add_argument("--report", action="store_true", help="Generate HTML report(s)")
    args = parser.parse_args()

    targets = []
    if args.file:
        with open(args.file) as f:
            targets = [line.strip() for line in f]
    elif args.target:
        targets = [args.target]
    else:
        parser.print_help()
        sys.exit(1)

    web_tools = args.tools.split(",") if args.tools else ["nikto", "dirb", "gobuster", "feroxbuster", "ffuf"]
    sub_tools = args.subtools.split(",") if args.subtools else ["ffuf", "dnsx", "sublist3r", "subfinder"]
    combined_files = []
    is_only = args.nmap_only or args.web_only or args.subdomain_only

    for target in targets:
        files = []
        open_ports = ""

        if (is_only and args.nmap_only) or not args.no_nmap: # if run nmap
            open_file = run_nmap(target)
            files.append(open_file)
            open_ports = extract_open_ports(open_file)
            if open_ports:
                svc_file = run_nmap_services(target, open_ports)
                files.append(svc_file)

        if not args.subdomain_only:
            web_ports = detect_web_ports(open_ports) if open_ports else ["80"]
            for port in web_ports:
                for tool in web_tools:
                    run_web_tool(tool)
                    files.append(f"{target}_port{port}_{tool}.txt")

        if not args.web_only:
            def run_sub(tool): run_subdomain_tool(tool, target, args.subwordlist)
            for tool in sub_tools:
                run_sub(tool)
                files.append(f"{target}_subdomains_{tool}.txt")

        if args.report:
            generate_html_report(target, files)
            combined_files.extend(files)

    if args.report and len(targets) > 1:
        generate_html_report("All_Targets", combined_files, combined=True)

if __name__ == "__main__":
    main()
