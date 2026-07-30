import requests, sys

HOST = "panorama.slmbank.local"
KEY = "your_api_key"

cmds = {
    "lock": "<request><commit-lock><add></add></commit-lock></request>",
    "unlock": "<request><commit-lock><remove></remove></commit-lock></request>",
    "status": "<show><commit-lock></commit-lock></show>",
}

action = sys.argv[1]  # lock / unlock / status
r = requests.get(f"https://{HOST}/api/", params={"type": "op", "cmd": cmds[action], "key": KEY}, verify=False)
print(r.text)
