# import streamlit as st
# from commit_lock import build_cmd, call_api, parse_response
# import os

# st.title("Panorama Ops Console")

# action = st.selectbox("Action", ["status", "lock", "unlock"])
# comment = st.text_input("Comment (lock only)") if action == "lock" else None

# if st.button("Run"):
#     key = os.environ.get("PANO_KEY")
#     cmd = build_cmd(action, comment)
#     xml_text = call_api("panorama.internal.slmbank.net", key, cmd)
#     st.code(xml_text)


import streamlit as st
import xml.etree.ElementTree as ET
import requests
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HOST = "host"

def build_cmd(action, comment=None):
    if action == "lock":
        if comment:
            return f"<request><commit-lock><add><comment>{comment}</comment></add></commit-lock></request>"
        return "<request><commit-lock><add></add></commit-lock></request>"
    if action == "unlock":
        return "<request><commit-lock><remove></remove></commit-lock></request>"
    if action == "status":
        return "<show><commit-locks></commit-locks></show>"

def call_api(host, key, cmd):
    r = requests.get(
        f"https://{host}/api/",
        params={"type": "op", "cmd": cmd, "key": key},
        verify=False,
        timeout=15,
    )
    return r.text

def parse_response(xml_text, action):
    root = ET.fromstring(xml_text)
    status = root.get("status")

    if action == "status":
        entries = root.findall(".//entry")
        if not entries:
            return "success", "No commit lock held by anyone."
        lines = []
        for e in entries:
            name = e.get("name", "unknown")
            comment = e.findtext("comment") or ""
            line = f"🔒 Lock held by: **{name}**"
            if comment:
                line += f"  \n💬 Comment: {comment}"
            lines.append(line)
        return "success", "\n\n".join(lines)

    if status == "success":
        return "success", f"{action.upper()} succeeded."
    else:
        msg = root.findtext(".//msg/line") or root.findtext(".//msg") or "unknown error"
        return "error", f"{action.upper()} failed: {msg}"


st.title("Panorama Ops Console")

action = st.selectbox("Action", ["status", "lock", "unlock"])
comment = st.text_input("Comment (lock only)") if action == "lock" else None

if st.button("Run"):
    key = os.environ.get("PANO_KEY")
    if not key:
        st.error("PANO_KEY environment variable not set.")
    else:
        cmd = build_cmd(action, comment)
        xml_text = call_api(HOST, key, cmd)
        result_status, message = parse_response(xml_text, action)

        if result_status == "success":
            st.success(message)
        else:
            st.error(message)

        with st.expander("Raw XML response"):
            st.code(xml_text, language="xml")
