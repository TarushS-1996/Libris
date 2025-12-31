import os
import streamlit as st


def st_folder_selector(
    label: str = "Select a folder",
    start_path: str = ".",
    key: str = "folder_selector",
):
    """
    Streamlit-based folder selector using dropdown navigation.
    Returns selected folder path or None.
    """

    if key not in st.session_state:
        st.session_state[key] = os.path.abspath(start_path)

    current_path = st.session_state[key]

    try:
        entries = [
            d for d in os.listdir(current_path)
            if os.path.isdir(os.path.join(current_path, d))
        ]
    except PermissionError:
        st.error("Permission denied.")
        return None

    entries = sorted(entries)
    entries.insert(0, "..")

    selected = st.selectbox(
        label,
        options=entries,
        key=f"{key}_select",
    )

    if selected == "..":
        parent = os.path.dirname(current_path)
        if parent and parent != current_path:
            st.session_state[key] = parent
        st.rerun()

    else:
        next_path = os.path.join(current_path, selected)
        if os.path.isdir(next_path):
            st.session_state[key] = next_path
            st.rerun()

    return current_path
