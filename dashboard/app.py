import streamlit as st

st.set_page_config(page_title="AspectLens", layout="wide", page_icon="📊")

pages = {
    "AspectLens": [
        st.Page("views/overview.py", title="Overview", icon="📊"),
        st.Page("views/department_view.py", title="Department View", icon="🏛️"),
        st.Page("views/faculty_drilldown.py", title="Faculty Drilldown", icon="🔍"),
        st.Page("views/upload_data.py", title="Upload Data", icon="📤"),
    ]
}

pg = st.navigation(pages)
pg.run()