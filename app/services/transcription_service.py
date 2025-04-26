import os
import logging
import google.generativeai as genai
from app.services.gemini_service import configure_gemini

logger = logging.getLogger(__name__)

class TranscriptionService:
    def __init__(self):
        # Configure Gemini if needed
        configure_gemini()
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    def transcribe(self, audio_path):
        """
        Transcribe audio file to text using Gemini directly.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            The transcribed text as a string
        """
        try:
            # For debugging
            logger.info(f"Starting transcription of audio file: {audio_path}")
            
            # Check if the audio file exists and has content
            if not os.path.exists(audio_path):
                logger.error(f"Audio file does not exist: {audio_path}")
                return "Error: Audio file not found."
                
            if os.path.getsize(audio_path) == 0:
                logger.error(f"Audio file is empty: {audio_path}")
                return "Error: Audio file is empty."
            
            # Get file extension for the MIME type
            file_ext = os.path.splitext(audio_path)[1].lower()
            
            # Determine the MIME type
            if file_ext == '.webm':
                mime_type = "audio/webm"
            elif file_ext == '.m4a':
                mime_type = "audio/m4a"
            elif file_ext == '.mp3':
                mime_type = "audio/mp3"
            elif file_ext == '.wav':
                mime_type = "audio/wav"
            elif file_ext == '.ogg':
                mime_type = "audio/ogg"
            elif file_ext == '.flac':
                mime_type = "audio/flac"
            else:
                # Default to octet-stream
                mime_type = "application/octet-stream"
            
            # Read the file
            logger.info(f"Reading audio file with MIME type: {mime_type}")
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            
            # Create a prompt for transcription only
            prompt = """
            Please transcribe the audio content accurately.
            Return ONLY the transcribed text, without any additional commentary.
            """
            
            # Send to Gemini
            logger.info("Sending to Gemini for transcription...")
            response = self.model.generate_content([prompt, {"mime_type": mime_type, "data": audio_data}])
            
            # Extract just the transcription
            transcription = response.text.strip()
            logger.info(f"Transcription received: {transcription[:50]}...")
            
            # If we got a very short or empty transcription, use a fallback response
            if len(transcription) < 5:
                logger.warning("Transcription is too short, using fallback")
                return "I couldn't properly hear the audio. Please speak clearly and try again."
            
            return transcription
            
        except Exception as e:
            logger.error(f"Error transcribing audio file: {e}")
            # Return a friendly error message
            return "I'm having trouble processing the audio. Please try again or speak more clearly."