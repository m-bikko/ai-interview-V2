# Audio Processing in AI Interview

This document explains how audio processing works in the AI Interview application and details the requirements for handling various audio formats.

## Supported Audio Formats

The application supports the following audio formats:
- MP3 (.mp3)
- WAV (.wav)
- OGG (.ogg)
- FLAC (.flac)
- WebM (.webm)
- M4A (.m4a)

## How It Works

The audio processing has been simplified to use Google's Gemini AI directly:

1. **Direct Audio Processing**: 
   - The application sends audio files directly to Gemini API
   - No more need for FFmpeg or intermediate conversion steps

2. **Python Dependencies**: 
   - The only required dependency is the Google Generative AI Python library (`google-generativeai`)

## Audio Processing Flow

When an audio is recorded during an interview:
1. Audio file is captured (.m4a, .webm, etc.)
2. The file is sent directly to Gemini API for transcription
3. The transcribed text is then processed by Gemini to provide interview feedback
4. Results are displayed to the user

## Benefits of the New Approach

1. **Simplified Setup**: No need to install FFmpeg or other external dependencies
2. **Better Performance**: Direct processing by Gemini reduces latency and potential errors
3. **Enhanced Accuracy**: Gemini provides high-quality transcription for multiple languages
4. **Error Resilience**: Better handling of poor audio quality with more graceful fallbacks

## Troubleshooting

If you encounter issues with audio processing:

1. Verify that the audio file is not corrupted
2. Make sure the audio file is not empty
3. Ensure your Google API key is valid and has access to Gemini models
4. Check that your internet connection is stable
5. Review application logs for specific error messages

## Manual Testing

You can test audio processing with the `direct_gemini_test.py` script:

```
python direct_gemini_test.py
```

This script will process audio files from the `./audio-test` directory and show the transcription and Gemini's response.