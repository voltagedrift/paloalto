import streamlit as st
from commit_lock import build_cmd, call_api, parse_response
import os

st.title("Panorama Ops Console")

action = st.selectbox("Action", ["status", "lock", "unlock"])
comment = st.text_input("Comment (lock only)") if action == "lock" else None

if st.button("Run"):
    key = os.environ.get("PANO_KEY")
    cmd = build_cmd(action, comment)
    xml_text = call_api("panorama.internal.slmbank.net", key, cmd)
    st.code(xml_text)
