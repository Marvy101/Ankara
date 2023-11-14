import streamlit as st

# Initialize Streamlit app
st.set_page_config(page_title='Ankara Narration AI')

st.title('Ankara AI', anchor='center')

st.markdown("""
    Welcome to Ankara AI! We have some exciting news. 
    We've moved to a brand new home! 
    Simply upload a video, choose a voice, and enter a narration prompt. 
    Ankara AI will do the rest!
""", unsafe_allow_html=True)

st.markdown("""
    To experience the new and improved Ankara AI, click the button below to be redirected to our new site.
""", unsafe_allow_html=True)

if st.button('Go to New Site'):
    st.markdown("[Click here to go to the new site](https://ankarawebsite.vercel.app/)")