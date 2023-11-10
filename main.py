import streamlit as st
import cv2
import base64
import time
import openai
import requests
from io import BytesIO
import tempfile
from tempfile import NamedTemporaryFile
import os
from pyht import Client
from dotenv import load_dotenv
from pyht.client import TTSOptions



# Future Things
# Copy only text
# Better AI Voice? More realistic or Voice of Celebrities
# Real time. Idea here is concatenate response so next prompt will start from ending of previous prompt
# Add voice (super fast voice would be awesome for commentary): https://www.ycombinator.com/launches/Jg8-playht-2-0-turbo-the-fastest-generative-ai-text-to-speech-api-yc-deal 

OPENAIKEY = st.secrets["general"]["OPENAI_KEY"]
HT_USER_ID = st.secrets["general"]["HT_USER_ID"]
HT_KEY = st.secrets["general"]["HT_KEY"]

# Initialize Streamlit app
st.set_page_config(page_title='Ankara Narration AI')

st.title('Ankara AI', anchor='center')
st.markdown("""
    Welcome to Ankara AI! This application uses artificial intelligence to generate narrations for your videos. 
    Simply upload a video, choose a voice, and enter a narration prompt. 
    Ankara AI will do the rest!
""", unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader("Upload a video", type=["mp4", "avi", "mov"])
voice_option = st.selectbox("Choose a voice", ["alloy", "echo", "fable", "onyx", "nova",  "shimmer"])  # Add more voice options as needed

@st.cache_data
def process_video(uploaded_file):

    # Create a temporary file with a specific name, this will give us the path
    tfile = tempfile.NamedTemporaryFile(delete=False)  # Set delete=False so it's not deleted after closing
    tfile.write(uploaded_file.read())  # Write the BytesIO stream to the temporary file
    tfile.close()  # Close the file (it will not be deleted due to delete=False)
    
    videoPath = tfile.name  # This is the path to the saved video file
    #st.write(f"The video is temporarily saved to {video_path}")

    # When a file is uploaded
    if uploaded_file is not None:
        # Read the video file
        video = cv2.VideoCapture(videoPath)

        base64Frames = []
        while video.isOpened():
            success, frame = video.read()
            if not success:
                break
            _, buffer = cv2.imencode(".jpg", frame)
            base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

        video.release()
        print(len(base64Frames), "frames read.")

        # Calculate video length
        video = cv2.VideoCapture(videoPath)
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = video.get(cv2.CAP_PROP_FPS)
        if fps != 0:
            video_length = frame_count / fps
        else:
            video_length = 0
        video.release()
        print("Video length:", video_length, "seconds")

        # Your existing code to process the video...
        return videoPath, base64Frames, video_length

prePrompt = "OUTPUT ONLY THE SCRIPT. REDUCE OR INCREASE SCRIPT LENGTH BASED ON THE LENGTH OF THE VIDEO AND ESTIMATED NARRATION TIME OF SCRIPT. Use caps and exclamation marks where needed to communicate excitement. "
inputPrompt = st.text_input("Enter the narration prompt")

if uploaded_file is not None and st.button('Generate Ankara') and inputPrompt:
        videoPath, base64Frames, video_length = process_video(uploaded_file)
                # Show the video player for the user to click play or not
        st.video(videoPath)

         # Generate the voiceover script using OpenAI
        Prompt = "These are the frames of a video. Create a narration according to the attached prompt from the text. The Language is English." + inputPrompt
        print('Number of Frames read: ', len(base64Frames[0::int(round(len(base64Frames)/10))]))
        PROMPT_MESSAGES = [
            {
                "role": "user",
                "content": [
                    prePrompt + Prompt + ' length of video: ' + str(video_length) + ' seconds',
                    *map(lambda x: {"image": x, "resize": 768}, base64Frames[0::int(round(len(base64Frames)/10))]),
                ],
            },
        ]
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAIKEY}"
                    }

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": PROMPT_MESSAGES,
             "max_tokens": 500
                }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        result = response.json()
        
        script_content = result['choices'][0]['message']['content']
        
        st.write("Generated Script: \n"+script_content)

        # Get the number of tokens used for billing purposes
        num_tokens = result['usage']['total_tokens']
        print(f"The output contains {num_tokens} tokens.")

        # Generate the audio using playht
        load_dotenv()

        client = Client(
            user_id=HT_USER_ID,
            api_key=HT_KEY,
                    )
        
        audio = b""
        options = TTSOptions(voice="s3://voice-cloning-zero-shot/d9ff78ba-d016-47f6-b0ef-dd630f59414e/female-cs/manifest.json")
        for chunk in client.tts(script_content, options):
            # do something with the audio chunk
            print(type(chunk))
            audio += chunk

        # Create a temporary file to store the audio data
        taudio = tempfile.NamedTemporaryFile(delete=False)
        try:
            taudio.write(audio)
            taudio.close()  # Make sure to close the file to flush the buffer and write the contents to disk

            st.download_button(
                label="Download audio",
                data=audio,
                file_name="AnkaraNarrator.mp3",
                mime="audio/mp3"
            )
        finally:
            # It is important to clean up the temporary file by deleting it when you are done with it
            # If you set delete=True when creating the NamedTemporaryFile, this would be unnecessary
            os.unlink(taudio.name)
        # User input for the narration prompt

   

   