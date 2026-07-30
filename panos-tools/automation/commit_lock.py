import requests
import xml.etree.ElementTree as ET # to see neat output without XML
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # to disable cert warnings

HOST = "host"
KEY = "your_api_key"

cmds = {
    "lock":   "<request><commit-lock><add></add></commit-lock></request>",
    "unlock": "<request><commit-lock><remove></remove></commit-lock></request>",
    "status": "<show><commit-locks></commit-locks></show>",
}

def call(action):
    r = requests.get(
        f"https://{HOST}/api/",
        params={"type": "op", "cmd": cmds[action], "key": KEY},
        verify=False,
    )
    return r.text

def parse(xml_text, action):
    root = ET.fromstring(xml_text)
    status = root.get("status")

    if action == "status":
        entries = root.findall(".//entry")
        if not entries:
            print("No commit lock held by anyone.")
            return
        for e in entries:
            name = e.get("name", "unknown")
            comment = e.findtext("comment") or ""
            print(f"Lock held by: {name}" + (f" | comment: {comment}" if comment else ""))
        return

    # lock / unlock actions
    if status == "success":
        print(f"{action.upper()} succeeded.")
    else:
        msg = root.findtext(".//msg/line") or root.findtext(".//msg") or "unknown error"
        print(f"{action.upper()} failed: {msg}")

if __name__ == "__main__":
    import sys
    action = sys.argv[1]
    xml_text = call(action)
    parse(xml_text, action)
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
