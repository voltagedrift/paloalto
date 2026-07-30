import argparse
import sys
import requests
import urllib3
import xml.etree.ElementTree as ET

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HOST = "host"
KEY_ENV_VAR = "PANO_KEY"


def build_cmd(action, comment=None):
    if action == "lock":
        if comment:
            return f"<request><commit-lock><add><comment>{comment}</comment></add></commit-lock></request>"
        return "<request><commit-lock><add></add></commit-lock></request>"
    if action == "unlock":
        return "<request><commit-lock><remove></remove></commit-lock></request>"
    if action == "status":
        return "<show><commit-locks></commit-locks></show>"
    raise ValueError(f"Unknown action: {action}")


def call_api(host, key, cmd):
    r = requests.get(
        f"https://{host}/api/",
        params={"type": "op", "cmd": cmd, "key": key},
        verify=False,
        timeout=15,
    )
    r.raise_for_status()
    return r.text


def parse_response(xml_text, action):
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
            line = f"Lock held by: {name}"
            if comment:
                line += f" | comment: {comment}"
            print(line)
        return

    if status == "success":
        print(f"{action.upper()} succeeded.")
    else:
        msg = root.findtext(".//msg/line") or root.findtext(".//msg") or "unknown error"
        print(f"{action.upper()} failed: {msg}")


def main():
    parser = argparse.ArgumentParser(description="Panorama commit-lock manager")
    parser.add_argument("action", choices=["lock", "unlock", "status"])
    parser.add_argument("--comment", help="Optional comment when locking")
    parser.add_argument("--host", default=HOST, help="Panorama hostname")
    parser.add_argument("--key", help="API key (overrides PANO_KEY env var)")
    args = parser.parse_args()

    key = args.key or __import__("os").environ.get(KEY_ENV_VAR)
    if not key:
        sys.exit(f"No API key provided. Set {KEY_ENV_VAR} env var or use --key.")

    cmd = build_cmd(args.action, args.comment)
    xml_text = call_api(args.host, key, cmd)
    parse_response(xml_text, args.action)


if __name__ == "__main__":
    main()
