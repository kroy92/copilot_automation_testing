import json
import os

from dotenv import load_dotenv
from openai import AzureOpenAI
from pydantic import BaseModel


class ComparisonScore(BaseModel):
    score: float
    reason: str
    decision: str


class SemanticSimilarityClient:
    def __init__(self, azure_openai_endpoint, azure_openai_key, deployment_name, api_version="2022-03-01-preview"):
        """
        Initialize the Azure OpenAI client for semantic similarity evaluation.
        """
        self.client = AzureOpenAI(
            azure_endpoint=azure_openai_endpoint,
            api_key=azure_openai_key,
            api_version=api_version
        )
        self.deployment_name = deployment_name

    def get_similarity_score(self, expected, actual):
        """
        Fetch semantic similarity score between expected and actual responses.
        """
        prompt = f"""
        Text 1: {expected}
        Text 2: {actual}
        """

        response = self.client.beta.chat.completions.parse(
            model=self.deployment_name,
            messages=[
                {"role": "system", "content": "You are an AI model specialized in evaluating the semantic similarity "
                                              "between two text statements. Your response must strictly adhere to "
                                              "JSON format, containing three components: \n\n1. **'Similarity "
                                              "Score'**: A numeric value between 0.0 (completely different) and 1.0 ("
                                              "identical), reflecting the degree of semantic similarity.\n2. "
                                              "**'Decision'**: Categorize the relationship between the statements. "
                                              "Choose one of the following options:\n   - 'Identical'\n   - "
                                              "'Similar'\n   - 'Somewhat Similar'\n   - 'Not Similar'\n   - "
                                              "'Completely Different'\n3. **'Reason'**: Provide a concise explanation "
                                              "for the assigned similarity score and decision, focusing on factual "
                                              "alignment, meaning, and context over minor wording "
                                              "differences.\n\nYour evaluations should prioritize accuracy and "
                                              "completeness while maintaining consistency across similar inputs. "
                                              "Factual alignment and overall meaning are your primary considerations, "
                                              "with less importance placed on superficial or stylistic "
                                              "differences.\n\n# Steps\n\n1. Compare the main ideas and meanings of "
                                              "the two statements.\n2. Assess the level of agreement or alignment in "
                                              "factual content, context, and purpose.\n3. Quantify the degree of "
                                              "semantic similarity as a numerical score (0.0 - 1.0).\n4. Use the "
                                              "similarity score to decide on a category from the defined list ("
                                              "'Identical', 'Similar', etc.).\n5. Provide a reason, ensuring it "
                                              "justifies both the similarity score and the corresponding "
                                              "decision.\n\n# Output Format\n\nYour response must follow this JSON "
                                              "structure:\n\n```json\n{\n  \"Similarity Score\": [numeric value "
                                              "between 0.0 and 1.0],\n  \"Decision\": \"[one of: 'Identical', "
                                              "'Similar', 'Somewhat Similar', 'Not Similar', 'Completely "
                                              "Different']\",\n  \"Reason\": \"[concise explanation of the similarity "
                                              "score and decision based on factual alignment and overall "
                                              "meaning]\"\n}\n```\n\nEnsure consistent formatting and avoid "
                                              "outputting anything outside the JSON structure.\n\n# Examples\n\n### "
                                              "Example 1:\n**Input Statements:**\n- Statement 1: \"Cats are small, "
                                              "domesticated mammals often kept as pets.\"\n- Statement 2: \"Felines "
                                              "are commonly kept as pets and are small, domesticated "
                                              "animals.\"\n\n**Output:**\n```json\n{\n  \"Similarity Score\": 0.85,"
                                              "\n  \"Decision\": \"Similar\",\n  \"Reason\": \"Both statements "
                                              "describe cats as small, domesticated mammals commonly kept as pets, "
                                              "with slight differences in phrasing.\"\n}\n```\n\n---\n\n### Example "
                                              "2:\n**Input Statements:**\n- Statement 1: \"The Eiffel Tower is "
                                              "located in Paris, France.\"\n- Statement 2: \"The Great Wall of China "
                                              "is a historic structure in China.\"\n\n**Output:**\n```json\n{\n  "
                                              "\"Similarity Score\": 0.1,\n  \"Decision\": \"Completely Different\","
                                              "\n  \"Reason\": \"The two statements refer to entirely different "
                                              "landmarks in different countries with no overlap in "
                                              "meaning.\"\n}\n```\n\n---\n\n### Example 3:\n**Input Statements:**\n- "
                                              "Statement 1: \"The Pacific Ocean is the largest ocean on Earth.\"\n- "
                                              "Statement 2: \"The Atlantic Ocean is smaller than the Pacific but "
                                              "larger than the Indian Ocean.\"\n\n**Output:**\n```json\n{\n  "
                                              "\"Similarity Score\": 0.3,\n  \"Decision\": \"Somewhat Similar\","
                                              "\n  \"Reason\": \"Both statements refer to oceans and their relative "
                                              "sizes, but they discuss different oceans and emphasize different "
                                              "aspects.\"\n}\n```\n\n# Notes\n\n- Maintain consistency in evaluations "
                                              "and formatting across all responses.\n- If the factual alignment "
                                              "between statements is unclear or ambiguous, provide a cautious and "
                                              "well-reasoned explanation.\n- Avoid introducing biases or "
                                              "interpretations that are not directly supported by the provided "
                                              "statements."},

                {"role": "user", "content": prompt}
            ],
            response_format=ComparisonScore
        )

        return response.choices[0].message.content

    def assert_semantically(self, expected, actual, threshold=0.75):
        """
        Assert that the semantic similarity score is above the threshold.
        """
        response = self.get_similarity_score(expected, actual)
        response = json.loads(response)
        score = response["score"]
        # print(response)
        assert score >= threshold, f"Semantic similarity too low: {score:.2f}. Reason: {response['reason']} Actual: {actual}"
        return score


if __name__ == "__main__":
    load_dotenv()
    client = SemanticSimilarityClient(os.getenv("ENDPOINT_NAME"), os.getenv("API_KEY"), os.getenv("DEPLOYMENT_NAME"),os.getenv("API_VERSION"))
    print(client.assert_semantically("This is a test", "This is a sample test"))
