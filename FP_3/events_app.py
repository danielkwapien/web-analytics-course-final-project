import streamlit as st

pg = st.navigation([st.Page("page_genre.py"), st.Page("page_city.py")])
pg.run()