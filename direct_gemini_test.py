import os
import base64
from dotenv import load_dotenv
import google.generativeai as genai
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gemini_with_audio(audio_file_path):
    """
    Test sending audio directly to Gemini API.
    We'll use the model that directly supports audio content.
    """
    print(f"Testing audio file: {audio_file_path}")
    
    # Load the audio file
    try:
        with open(audio_file_path, 'rb') as f:
            audio_data = f.read()
            
        # Print file size
        print(f"Audio file size: {len(audio_data)} bytes")
        
        # Initialize the Gemini model
        # Use gemini-1.5-pro-latest or gemini-1.5-flash-latest which support multimodal content
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        
        # Create a prompt
        prompt = """
        This is an audio file. Please:
        1. Transcribe what you hear in the audio
        2. Provide a brief response to what was said
        """
        
        # Determine the MIME type based on file extension
        mime_type = "audio/webm" if audio_file_path.endswith('.webm') else "audio/m4a"
        
        # Generate content with audio
        response = model.generate_content([prompt, {"mime_type": mime_type, "data": audio_data}])
        
        print("\nGemini Response:")
        print("=" * 50)
        print(response.text)
        print("=" * 50)
        
        return response.text
        
    except Exception as e:
        logger.error(f"Error processing audio: {e}", exc_info=True)
        print(f"ERROR: {str(e)}")
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY not found in environment")
        print("ERROR: GOOGLE_API_KEY not found. Please set it in your .env file.")
        exit(1)
    
    # Configure Gemini
    try:
        genai.configure(api_key=api_key)
        print("Gemini API configured successfully")
    except Exception as e:
        logger.error(f"Error configuring Gemini API: {e}")
        print(f"ERROR: Failed to configure Gemini API: {e}")
        exit(1)
    
    # Test with WebM file
    webm_file = './audio-test/Новая запись 2.webm'
    test_gemini_with_audio(webm_file)
    
    # Test with M4A file
    m4a_file = './audio-test/Новая запись 2.m4a'
    test_gemini_with_audio(m4a_file)