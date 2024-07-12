import streamlit as st
import pandas as pd
import numpy as np
import pytz
from datetime import datetime
from datetime import date
from PIL import Image
from ercp_gpt import ERCP
from streamlit_autorefresh import st_autorefresh

# Initialize session state attributes at the beginning of your script
if 'reset' not in st.session_state:
    st.session_state.reset = False
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""
if 'result' not in st.session_state:
    st.session_state.result = ""  # Initialize an empty result

# Page settings and other initial configurations
st.set_page_config(layout="wide", page_title="Service Robot")
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
count = st_autorefresh(interval=5000, limit=100, key="fizzbuzzcounter")

# Split the page into two columns
col1, col2 = st.columns(2)

with col1:
    # Display the logo
    logo = Image.open('images/logo.png')
    logo = logo.resize((200, 200))
    st.image(logo, width=200)

    st.write("Search for Information")
    user_input = st.text_input("Enter your query:", value=st.session_state.user_input, key="prompt_field")
    search_button = st.button("Enter prompt")

    if search_button:
        with st.spinner('Searching...'):
            ercp = ERCP()
            query = user_input
            res = ercp.run_prog(query)
            st.session_state.result = res
            st.session_state.reset = True  # Indicate that reset was triggered

    # Display the result
    if st.session_state.result:
        st.write(st.session_state.result)
        st.session_state.user_input = ""  # Clear user input

with col2:
    st.write("Video and Information")
    # Placeholder for a video link
    video_url = "http://192.168.2.103:8080/"
    st.video(video_url)
    st.write("Here is some information about the video or other content.")
# #Time
# nowTime = datetime.now()
# current_time = nowTime.strftime("%H:%M:%S")
# today = str(date.today())
# # st.write(today)
# timeMetric,= st.columns(1)
# timeMetric.metric("",today)

# # Row A
# a1, a2, a3 = st.columns(3)
# a1.image(logo)
# a2.metric("Stockholm Temperature", f"", f""+"%")
# a3.metric("Stockholm time", current_time)


# # Row B
# b1, b2, b3, b4 = st.columns(4)
# b1.metric("Humidity", f""+"%")
# b2.metric("Feels like", f"")
# b3.metric("Highest temperature", f"")
# b4.metric("Lowest temperature", f"")

# # Row C
# #C1 being the graph, C2 The Table.
# c1, c2 = st.columns((7,3))

# #Graph:
# with c1:

#     chart_data = pd.DataFrame(
#          np.random.randn(20, 3),
#          columns=['Low', 'High', 'Close'])
#     st.line_chart(chart_data)

# #The fake nonsens table:
# with c2:
#     df = pd.DataFrame(
#         np.random.randn(7, 5),
#         columns=('Paris','Malta','Stockholm','Peru','Italy')
#     )

#     st.table(df)

# #Manually refresh button
# st.button("Run me manually")