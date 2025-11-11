import google.generativeai as genai
from app.config.settings import settings
import json
from typing import Dict, Optional

# Configure Gemini
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)


class GeminiService:
    @staticmethod
    def score_essay(essay_content: str, prompt_text: str, word_count: int) -> Dict:
        """
        Score an essay using Gemini AI based on IELTS/TOEFL rubrics

        Returns a dictionary with:
        - task_response_score (0-9)
        - coherence_cohesion_score (0-9)
        - lexical_resource_score (0-9)
        - grammatical_range_score (0-9)
        - overall_score (0-9)
        - feedback (structured feedback)
        """

        if not settings.gemini_api_key:
            # Return mock data for development
            return GeminiService._get_mock_feedback(word_count)

        try:
            model = genai.GenerativeModel('gemini-pro')

            scoring_prompt = f"""You are an expert IELTS/TOEFL writing examiner. Score the following essay based on these criteria:

1. Task Response (0-9): How well does the essay address the prompt?
2. Coherence and Cohesion (0-9): How well organized and connected is the writing?
3. Lexical Resource (0-9): Vocabulary range and accuracy
4. Grammatical Range and Accuracy (0-9): Grammar variety and correctness

Essay Prompt:
{prompt_text}

Essay (Word count: {word_count}):
{essay_content}

Provide your response in the following JSON format:
{{
    "task_response_score": <score 0-9>,
    "coherence_cohesion_score": <score 0-9>,
    "lexical_resource_score": <score 0-9>,
    "grammatical_range_score": <score 0-9>,
    "overall_score": <average of above scores>,
    "feedback": {{
        "strengths": ["strength 1", "strength 2", "strength 3"],
        "weaknesses": ["weakness 1", "weakness 2", "weakness 3"],
        "task_response": "Detailed feedback on task response",
        "coherence_cohesion": "Detailed feedback on coherence and cohesion",
        "lexical_resource": "Detailed feedback on vocabulary",
        "grammatical_range": "Detailed feedback on grammar",
        "suggestions": ["specific suggestion 1", "specific suggestion 2", "specific suggestion 3"],
        "revised_outline": "A brief outline showing how to improve the essay structure"
    }}
}}

Be specific, constructive, and encouraging. Focus on actionable improvements."""

            response = model.generate_content(scoring_prompt)

            # Parse the JSON response
            response_text = response.text.strip()

            # Extract JSON from markdown code blocks if present
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            result = json.loads(response_text)
            return result

        except Exception as e:
            print(f"Error scoring essay with Gemini: {e}")
            # Return mock data as fallback
            return GeminiService._get_mock_feedback(word_count)

    @staticmethod
    def _get_mock_feedback(word_count: int) -> Dict:
        """Generate mock feedback for development/testing"""
        # Simple scoring based on word count
        length_score = 7.0 if 200 <= word_count <= 300 else 5.5

        return {
            "task_response_score": length_score,
            "coherence_cohesion_score": 6.5,
            "lexical_resource_score": 6.0,
            "grammatical_range_score": 6.5,
            "overall_score": 6.5,
            "feedback": {
                "strengths": [
                    "Clear thesis statement",
                    "Appropriate essay length",
                    "Good paragraph structure"
                ],
                "weaknesses": [
                    "Limited vocabulary range",
                    "Some repetitive sentence structures",
                    "Could use more specific examples"
                ],
                "task_response": "The essay addresses the main points of the prompt. Consider developing your arguments with more specific examples and deeper analysis.",
                "coherence_cohesion": "The essay has a logical structure with clear paragraphs. Work on using more transition words to improve flow between ideas.",
                "lexical_resource": "Vocabulary is adequate but somewhat repetitive. Try to use synonyms and more varied expressions to convey your ideas.",
                "grammatical_range": "Grammar is generally accurate with good use of complex sentences. Watch for subject-verb agreement in longer sentences.",
                "suggestions": [
                    "Add more specific examples to support your main arguments",
                    "Use a wider range of transition words (furthermore, moreover, consequently)",
                    "Vary your sentence openings to improve readability",
                    "Include counterarguments to strengthen your position"
                ],
                "revised_outline": "Introduction with clear thesis → Body paragraph 1 with specific example → Body paragraph 2 with data/statistics → Counterargument and rebuttal → Conclusion restating position"
            }
        }
