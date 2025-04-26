import os
import sys
from dotenv import load_dotenv
from app.services.transcription_service import TranscriptionService
from app.services.gemini_service import GeminiService, configure_gemini

def test_audio_processing(audio_file_path):
    """
    Test audio processing with Gemini
    """
    print(f"Testing audio file: {audio_file_path}")
    
    # Initialize services
    transcription_service = TranscriptionService()
    gemini_service = GeminiService()
    
    # Transcribe audio
    print("Transcribing audio...")
    transcription = transcription_service.transcribe(audio_file_path)
    print(f"Transcription result: {transcription}")
    
    # Send to Gemini
    print("\nSending to Gemini...")
    prompt = """
    Please analyze the following audio transcription and provide a brief response:
    
    "{}"
    
    Respond as if you're having a conversation with the speaker.
    """.format(transcription)
    
    response = gemini_service.generate_review(prompt)
    print("\nGemini response:")
    print(response)

if __name__ == "__main__":
    # Make sure environment variables are loaded
    load_dotenv()
    
    # Configure Gemini
    configure_gemini()
    
    # Test directory
    audio_test_dir = './audio-test'
    
    # Get the audio files
    webm_file = os.path.join(audio_test_dir, 'Новая запись 2.webm')
    m4a_file = os.path.join(audio_test_dir, 'Новая запись 2.m4a')
    
    # Test webm file
    print("=" * 50)
    print("TESTING WEBM FILE")
    print("=" * 50)
    test_audio_processing(webm_file)
    
    # Test m4a file
    print("\n\n" + "=" * 50)
    print("TESTING M4A FILE")
    print("=" * 50)
    test_audio_processing(m4a_file)