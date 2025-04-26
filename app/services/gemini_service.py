import google.generativeai as genai
import os
import logging
import functools
from dotenv import load_dotenv
from flask import current_app

logger = logging.getLogger(__name__)

# Global flag to avoid multiple reconfigurations
_gemini_configured = False

def configure_gemini():
    """Loads API key and configures the Gemini client."""
    global _gemini_configured
    if _gemini_configured:
        return True
        
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        logger.error("ERROR: GOOGLE_API_KEY environment variable not set.")
        raise ValueError("GOOGLE_API_KEY environment variable is required.")
    else:
        try:
            genai.configure(api_key=api_key)
            logger.info("Gemini API configured successfully.")
            _gemini_configured = True
            return True
        except Exception as e:
            logger.error(f"ERROR: Failed to configure Gemini API: {e}")
            raise

class GeminiService:
    def __init__(self, model_name='gemini-1.5-flash-latest'):
        """Initializes the Gemini Service."""
        try:
            self.model_name = model_name
            self._model = genai.GenerativeModel(self.model_name)
            logger.info(f"GeminiService initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Model ({self.model_name}): {e}", exc_info=True)
            raise
    
    def generate_review(self, prompt_text, safety_settings=None, generation_config=None, retries=2):
        """
        Generates content using the configured Gemini model.
        
        Args:
            prompt_text: The complete prompt to send to the Gemini API.
            safety_settings: Optional safety settings.
            generation_config: Optional generation config (temperature, max_tokens etc).
            retries: Number of retries in case of rate limit or transient errors.
            
        Returns:
            The generated text content as a string, or None if an error occurs.
        """
        import time
        
        for attempt in range(retries + 1):
            try:
                logger.debug(f"Sending prompt to Gemini ({self.model_name}):\n{prompt_text[:200]}...")
                
                # Default generation config if none provided
                if not generation_config:
                    generation_config = {
                        'temperature': 0.7,
                        'max_output_tokens': 2048,
                    }
                
                # Prepare optional configurations
                kwargs = {}
                if safety_settings:
                    kwargs['safety_settings'] = safety_settings
                kwargs['generation_config'] = generation_config
                
                # Call the API
                response = self._model.generate_content(prompt_text, **kwargs)
                
                # Basic check on response structure
                if response and hasattr(response, 'text'):
                    logger.debug(f"Received Gemini response (first 100 chars): {response.text[:100]}")
                    return response.text
                elif response and hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                    logger.warning(f"Gemini content generation blocked. Feedback: {response.prompt_feedback}")
                    return f"Error: Content generation blocked due to safety settings ({response.prompt_feedback})."
                else:
                    logger.error(f"Received unexpected or empty response from Gemini API. Response: {response}")
                    return "Error: Received an unexpected or empty response from the AI."
                    
            except Exception as e:
                error_message = str(e).lower()
                
                # Check if this is a rate limit error or server error (5xx)
                if "rate limit" in error_message or "429" in error_message or "500" in error_message:
                    if attempt < retries:
                        wait_time = (attempt + 1) * 2  # Exponential backoff: 2s, 4s, etc.
                        logger.warning(f"Rate limit or server error, retrying in {wait_time}s... ({attempt+1}/{retries})")
                        time.sleep(wait_time)
                        continue
                
                logger.error(f"Gemini API call failed: {e}", exc_info=True)
                return f"Error: AI service encountered an issue ({type(e).__name__}). Please try again later."
    
    def create_interview_review_prompt(self, question, answer, profession, grade):
        """Creates a prompt for Gemini to review an interview answer."""
        prompt = f"""
        Analyze the following interview answer based on the provided question, profession, and grade level.
        
        **Profession:** {profession}
        **Grade Level:** {grade}
        **Interview Question:**
        "{question}"
        
        **Candidate's Answer (Transcribed Audio):**
        "{answer}"
        
        **Instructions for AI Analysis:**
        Act as an experienced IT interviewer or technical hiring manager for the specified role and level. Evaluate the candidate's answer based on the following criteria:
        1. **Technical Accuracy:** Is the information correct and technically sound for the given {profession} ({grade}) role?
        2. **Relevance:** Does the answer directly address the question asked?
        3. **Clarity and Conciseness:** Is the answer easy to understand? Does it avoid unnecessary jargon or rambling?
        4. **Completeness:** Does the answer cover the key aspects expected for this question at a {grade} level? Mention any missing key points.
        5. **Structure:** Is the answer well-organized?
        
        **Output Format:**
        Provide feedback in the following structure:
        **Overall Assessment:** [Provide a brief, 1-2 sentence summary of the answer's quality.]
        **Strengths:**
        - [List specific strengths, e.g., "Good explanation of X concept."]
        - [Another strength.]
        **Areas for Improvement:**
        - [List specific weaknesses or areas needing more detail/clarity, e.g., "Could elaborate more on Y."]
        - [Suggest specific ways to improve the answer.]
        **Technical Score (Estimate):** [Provide an estimated score from 1.0 (Poor) to 5.0 (Excellent) based ONLY on the technical content and clarity of this single answer, considering the role/level.]
        
        **Important:** Focus solely on the provided question and answer. Be constructive and provide actionable feedback. If the answer is completely irrelevant or nonsensical, state that clearly. Do not invent information not present in the answer.
        """
        return prompt
    
    def create_cv_review_prompt(self, cv_text):
        """Creates a prompt for Gemini to review extracted CV text."""
        prompt = f"""
        Analyze the following text extracted from a candidate's CV (Resume). Assume the candidate is likely applying for roles in the IT industry (Software Development, Data Science, DevOps, Product Management, Design etc.).
        
        **Extracted CV Text:**
        --- Start of CV Text ---
        {cv_text}
        --- End of CV Text ---
        
        **Instructions for AI Analysis:**
        Act as an experienced IT recruiter and career advisor. Review the provided CV text thoroughly. Focus on content, structure (as inferrable from text flow), and overall presentation based *only* on the text provided.
        **Output Format:**
        Provide a structured review with the following sections:
        **Overall Impression:** [A brief summary (2-3 sentences) of the CV's effectiveness and target role suitability based on the content.]
        **Strengths:**
        - [List specific strong points, key skills highlighted, notable achievements mentioned, e.g., "Clear project descriptions with measurable results."]
        - [Another strength.]
        **Weaknesses / Areas for Improvement:**
        - [Identify missing key sections (e.g., missing contact info, lack of summary/objective if applicable), weak descriptions, lack of quantification.]
        - [Suggest specific improvements, e.g., "Quantify achievements in project X using numbers.", "Consider adding a concise professional summary."]
        **Clarity and Formatting (Inferred):** [Comment on the likely clarity and readability based on the text structure. Mention any red flags like very long paragraphs or inconsistent formatting suggested by the text.]
        **Keywords and Relevance:** [Mention prominent IT keywords found and comment on potential relevance to common IT roles.]
        
        **Important:** Base your analysis *only* on the provided text. Acknowledge if the text seems poorly extracted or incomplete. Be constructive and provide actionable advice for the candidate.
        """
        return prompt
    
    def review_interview_answer(self, question, answer, profession, grade):
        """Process an interview answer and generate a review."""
        prompt = self.create_interview_review_prompt(question, answer, profession, grade)
        return self.generate_review(prompt)
    
    def review_cv(self, cv_text):
        """Process a CV and generate a review."""
        prompt = self.create_cv_review_prompt(cv_text)
        return self.generate_review(prompt)