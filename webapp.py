import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import openai

# Assuming OPENAI_API_KEY is set as an environment variable
openai.api_key = st.secrets["OPENAI_API_KEY"]

def extract_video_id(url):
    """Extract the video ID from a YouTube URL."""
    return url.split('=')[-1]

def generate_question(text):
    """Generate a question based on the provided text using OpenAI's Chat Completions API."""
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Create a question based on the provided video transcript text."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip()

def provide_feedback(question, answer, transcript):
    """Provide feedback on the user's answer based on the transcript using OpenAI's Chat Completions API."""
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"You are a helpful UPSC teacher. Provide feedback to the user based on the following knowledge: {transcript}. The user was asked: {question}."},
            {"role": "user", "content": f"Answer: {answer}"}
        ]
    )
    return response.choices[0].message.content.strip()

st.title('Kaabil Demo: AI-Powered Video Learning Platform')
st.text('This is a demo of a video learning platform that uses AI to generate questions and provide feedback on user answers. Enter a YouTube video URL and the current playback time to get started.')
video_url = st.text_input('Enter YouTube Video URL:', '')

if video_url:
    video_id = extract_video_id(video_url)

    # Embed YouTube video using streamlit_player with dynamic start time
    current_time = st.number_input('Enter current playback time in seconds:', min_value=0, value=0)
    modified_video_url = f"https://www.youtube.com/embed/{video_id}?start={current_time}"
    from streamlit_player import st_player
    st_player(modified_video_url)

    # Generate and display question
    if st.button('Generate Question'):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'hi'])
            start_time = max(0, current_time - 180)  # Calculate last 3 minutes
            relevant_transcript = [t for t in transcript if start_time <= t['start'] <= current_time]
            transcript_text = " ".join([t['text'] for t in relevant_transcript])
            question = generate_question(transcript_text)
            st.session_state.question = question  # Save question to session state
            st.session_state.transcript_text = transcript_text  # Save transcript segment to session state
        except Exception as e:
            st.error(f"An error occurred: {e}")

    # Display saved question from session state
    if 'question' in st.session_state:
        st.write('Question:', st.session_state.question)
        answer = st.text_input('Your answer:', key="answer")

    # Generate and display feedback
    if st.button('Submit Answer') and 'answer' in st.session_state:
        feedback = provide_feedback(st.session_state.question, st.session_state.answer, st.session_state.transcript_text)
        st.write('Feedback on your answer:', feedback)

        # Optionally, clear the question and answer from session state after displaying feedback
        del st.session_state.question
        del st.session_state.answer