# alive.py
import streamlit as st
import streamlit.components.v1 as components

def app():
    st.header("Alive: Website Viewer")

    # Input for the URL
    url = st.text_input("Enter Website Link (include https://)", "https://www.wikipedia.org")

    st.write(f"Displaying: **{url}**")

    # The iframe component to render the external site
    # height=800 ensures a good viewing area
    try:
        components.iframe(url, height=800, scrolling=True)
    except Exception as e:
        st.error(f"Error loading website: {e}")