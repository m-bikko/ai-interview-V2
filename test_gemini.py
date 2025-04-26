import os
from dotenv import load_dotenv
from app.services.gemini_service import GeminiService, configure_gemini

def test_gemini_api():
    """Test the Gemini API with mock transcriptions"""
    # Initialize services
    gemini_service = GeminiService()
    
    # Mock transcriptions for testing
    mock_transcriptions = [
        "This is a test transcription from an m4a file.",
        "This is a test transcription from a webm file."
    ]
    
    for i, transcription in enumerate(mock_transcriptions):
        print(f"\nTesting with mock transcription {i+1}:")
        print(f"Transcription: {transcription}")
        
        # Send to Gemini
        prompt = """
        Please analyze the following audio transcription and provide a brief response:
        
        \"{}\"
        
        Respond as if you're having a conversation with the speaker.
        """.format(transcription)
        
        print("Sending to Gemini...")
        response = gemini_service.generate_review(prompt)
        print("\nGemini response:")
        print(response)

if __name__ == "__main__":
    # Make sure environment variables are loaded
    load_dotenv()
    
    # Configure Gemini
    configure_gemini()
    
    # Test Gemini API
    test_gemini_api()