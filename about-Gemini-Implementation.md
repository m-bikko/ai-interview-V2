Okay, here is a dedicated section focusing specifically on the **Gemini API Integration details** for the `README.md`. This section expands significantly on the overview provided earlier, offering implementation guidance.

---

## `README.md` Section: 10. Gemini API Integration - Implementation Details

This section details the specific implementation of the Google Generative AI (Gemini) API within the AI Interview platform.

### 10.1. Core Setup and Configuration

1.  **Library Installation:** Ensure the `google-generativeai` library is listed in `requirements.txt` and installed:
    ```bash
    pip install google-generativeai
    ```

2.  **API Key Management:**
    *   The API key **MUST** be provided via the `GOOGLE_API_KEY` environment variable.
    *   Use `python-dotenv` for local development to load the key from a `.env` file (which is **excluded** from Git via `.gitignore`).
    *   **Configuration Code:** In your application's initialization logic (e.g., `config.py`, `app/__init__.py`, or wherever the Flask/Django/FastAPI app is created), configure the library:
        ```python
        import google.generativeai as genai
        import os
        from dotenv import load_dotenv

        def configure_gemini():
            """Loads API key and configures the Gemini client."""
            load_dotenv() # Load environment variables from .env
            api_key = os.getenv("GOOGLE_API_KEY")

            if not api_key:
                print("ERROR: GOOGLE_API_KEY environment variable not set.")
                # Option 1: Raise an error to prevent app startup
                raise ValueError("GOOGLE_API_KEY environment variable is required.")
                # Option 2: Disable AI features (log a warning)
                # print("WARNING: Gemini API features will be disabled.")
                # return False # Indicate configuration failure
            else:
                try:
                    genai.configure(api_key=api_key)
                    print("Gemini API configured successfully.")
                    return True # Indicate success
                except Exception as e:
                    print(f"ERROR: Failed to configure Gemini API: {e}")
                    raise # Re-raise the exception for clarity or handle appropriately

        # Call this function during application startup
        # gemini_configured = configure_gemini()
        ```
    *   Store the success state (`gemini_configured`) or handle the exception so that API calls are only attempted if configuration succeeded.

3.  **Model Selection:**
    *   The designated model is `gemini-1.5-flash-latest`.
    *   Instantiate the model when needed:
        ```python
        # Within a service function that needs to call the API
        # if gemini_configured: # Check if setup was successful
        try:
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            # Proceed with model.generate_content(...)
        except Exception as e:
            # Handle potential errors during model instantiation if needed
            print(f"Error creating Gemini model instance: {e}")
            # Return an error or fallback
        ```

### 10.2. Service Layer Abstraction (Recommended)

It's highly recommended to encapsulate Gemini API interactions within a dedicated service module (e.g., `app/services/gemini_service.py` or integrated within `interview_service.py` and `cv_service.py`) rather than calling the API directly from route handlers/views.

```python
# Example structure in app/services/gemini_service.py
import google.generativeai as genai
import logging # Use proper logging

# Assume logger is configured elsewhere
logger = logging.getLogger(__name__)

# Assume configure_gemini() has been called successfully at startup

class GeminiService:
    def __init__(self, model_name='gemini-1.5-flash-latest'):
        """Initializes the Gemini Service."""
        try:
            # You might instantiate the model here or per-request
            # Instantiating per-request is simpler but potentially less efficient
            # Instantiating once requires careful state management if settings change
            self.model_name = model_name
            self._model = genai.GenerativeModel(self.model_name)
            logger.info(f"GeminiService initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Model ({self.model_name}): {e}", exc_info=True)
            raise # Re-raise or handle appropriately


    def generate_review(self, prompt_text: str, safety_settings=None, generation_config=None) -> str | None:
        """
        Generates content using the configured Gemini model.

        Args:
            prompt_text: The complete prompt to send to the Gemini API.
            safety_settings: Optional safety settings.
            generation_config: Optional generation config (temperature, max_tokens etc).

        Returns:
            The generated text content as a string, or None if an error occurs.
        """
        try:
            logger.debug(f"Sending prompt to Gemini ({self.model_name}):\n{prompt_text[:200]}...") # Log truncated prompt

            # Prepare optional configurations
            kwargs = {}
            if safety_settings:
                kwargs['safety_settings'] = safety_settings
            if generation_config:
                kwargs['generation_config'] = generation_config

            # Call the API
            response = self._model.generate_content(prompt_text, **kwargs)

            # Basic check on response structure (may need refinement based on API behavior)
            if response and hasattr(response, 'text'):
                 logger.debug(f"Received Gemini response (first 100 chars): {response.text[:100]}")
                 return response.text
            elif response and response.prompt_feedback:
                 # Handle cases where content is blocked
                 logger.warning(f"Gemini content generation blocked. Feedback: {response.prompt_feedback}")
                 return f"Error: Content generation blocked due to safety settings ({response.prompt_feedback})."
            else:
                 logger.error(f"Received unexpected or empty response from Gemini API. Response: {response}")
                 return "Error: Received an unexpected or empty response from the AI."


        except Exception as e:
            # Catch potential specific exceptions from google.api_core if needed
            # e.g., google.api_core.exceptions.ResourceExhausted: for rate limits
            # e.g., google.api_core.exceptions.InvalidArgument: for bad requests
            logger.error(f"Gemini API call failed: {e}", exc_info=True) # Log full traceback
            return f"Error: AI service encountered an issue ({type(e).__name__}). Please try again later."


# How to use it in another service:
# from .gemini_service import GeminiService
# gemini = GeminiService()
# review_text = gemini.generate_review("Your detailed prompt here")
```

### 10.3. Implementation for Interview Answer Review

1.  **Input Gathering:** The relevant route/service function receives:
    *   `question_text`: The exact text of the interview question.
    *   `transcribed_answer`: The text output from the chosen audio transcription method.
    *   `profession`: E.g., "Backend Developer".
    *   `grade`: E.g., "Senior".

2.  **Prompt Construction (Critical):** Create a clear, detailed prompt. Use f-strings or templating.
    ```python
    def create_interview_review_prompt(question: str, answer: str, profession: str, grade: str) -> str:
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
        1.  **Technical Accuracy:** Is the information correct and technically sound for the given {profession} ({grade}) role?
        2.  **Relevance:** Does the answer directly address the question asked?
        3.  **Clarity and Conciseness:** Is the answer easy to understand? Does it avoid unnecessary jargon or rambling?
        4.  **Completeness:** Does the answer cover the key aspects expected for this question at a {grade} level? Mention any missing key points.
        5.  **Structure:** Is the answer well-organized?

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
    ```

3.  **API Call:**
    ```python
    # Within the interview processing logic (e.g., inside a Flask route or a celery task)
    # Assume 'gemini_service' is an instance of GeminiService
    # Assume 'question', 'answer', 'profession', 'grade' are available

    prompt = create_interview_review_prompt(question, answer, profession, grade)
    review_text = gemini_service.generate_review(prompt)

    if review_text and not review_text.startswith("Error:"):
        # Process the review_text
        # 1. Store review_text in the database associated with the question attempt.
        # 2. Optionally: Parse the estimated score if needed for the overall rating.
        #    (Requires robust parsing, e.g., regex, as LLM output format can vary slightly)
        # 3. Prepare the feedback for display to the user.
        pass
    else:
        # Handle the error - log it, inform the user AI review failed
        print(f"Failed to get AI review. Result: {review_text}")
        # Store a placeholder or error message in the DB?
        pass
    ```

### 10.4. Implementation for CV Review

1.  **Input Gathering:** The relevant route/service function receives:
    *   `cv_text`: The full text content extracted from the uploaded PDF file.

2.  **Prompt Construction:**
    ```python
    def create_cv_review_prompt(cv_text: str) -> str:
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
    ```

3.  **API Call:**
    ```python
    # Within the CV processing logic (e.g., inside a background task after upload)
    # Assume 'gemini_service' is an instance of GeminiService
    # Assume 'extracted_cv_text' is available

    prompt = create_cv_review_prompt(extracted_cv_text)
    review_text = gemini_service.generate_review(prompt)

    if review_text and not review_text.startswith("Error:"):
        # Process the review_text
        # Store the full review_text in the database associated with the uploaded CV.
        # Prepare for display to the user.
        pass
    else:
        # Handle the error - log it, store an error message with the CV.
        print(f"Failed to get CV review. Result: {review_text}")
        # Update CV status in DB to indicate review failure.
        pass
    ```

### 10.5. Advanced Configuration (Optional)

*   **`GenerationConfig`:** Control model output parameters.
    ```python
    from google.generativeai.types import GenerationConfig

    # Example config
    config = GenerationConfig(
        temperature=0.7,    # Controls randomness (lower = more deterministic)
        max_output_tokens=1024, # Limit response length
        # top_p=0.9,        # Nucleus sampling
        # top_k=40          # Top-k sampling
    )
    # Pass to generate_review: gemini_service.generate_review(prompt, generation_config=config)
    ```
*   **`SafetySettings`:** Adjust content filtering thresholds. Be cautious changing defaults.
    ```python
    from google.generativeai.types import HarmCategory, HarmBlockThreshold

    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        # ... other categories
    }
    # Pass to generate_review: gemini_service.generate_review(prompt, safety_settings=safety_settings)
    ```

### 10.6. Error Handling Specifics

*   **API Errors:** Catch exceptions from `google.api_core.exceptions` if specific handling is needed (e.g., retrying on rate limits - `ResourceExhaustedError`, logging `InvalidArgumentError`).
*   **Blocked Content:** Check `response.prompt_feedback` if `response.text` is missing, as content might be blocked by safety filters. Log this information.
*   **Network Issues:** General `requests` or network-level exceptions should also be handled.
*   **Fallback:** Decide what happens if an API call fails. Should the user see an error? Should a default message be stored? Ensure the application remains functional even if the AI component fails temporarily. Implement appropriate logging for all failures.

---

This detailed breakdown should provide the AI agent with sufficient instructions to implement the Gemini API integration correctly and robustly within the context of the AI Interview project.