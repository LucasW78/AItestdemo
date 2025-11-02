"""
Gemini AI client for test case generation.
"""
import logging
import json
import asyncio
from typing import Dict, Any, Optional, List
import google.generativeai as genai

from app.config import settings

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Client for interacting with Google's Gemini AI model.
    """

    def __init__(self):
        """Initialize Gemini client with API key."""
        self.api_key = settings.gemini_api_key
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required")

        # Configure the API
        genai.configure(api_key=self.api_key)

        # Initialize the model
        self.model = genai.GenerativeModel(settings.gemini_model)

        # Safety settings
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]

        logger.info(f"Gemini client initialized with model: {settings.gemini_model}")

    async def generate_test_cases(
        self,
        context: str,
        requirements: Optional[str] = None,
        test_type: str = "functional",
        count: int = 10,
        priority: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate test cases based on document context and requirements.

        Args:
            context: Document context from RAG system
            requirements: Specific requirements to focus on
            test_type: Type of tests to generate (functional, performance, security, etc.)
            count: Number of test cases to generate
            priority: Default priority for generated test cases

        Returns:
            Dictionary containing generated test cases and metadata
        """
        try:
            # Construct the prompt
            prompt = self._build_test_case_prompt(context, requirements, test_type, count, priority)

            # Generate content
            logger.info(f"Generating {count} test cases of type: {test_type}")

            response = await self._generate_content_async(prompt)

            # Parse the response
            test_cases = self._parse_test_cases_response(response.text)

            # Add metadata
            for i, test_case in enumerate(test_cases):
                test_case.update({
                    "generation_context": context[:1000] + "..." if len(context) > 1000 else context,
                    "generation_requirements": requirements,
                    "generation_test_type": test_type,
                    "generation_priority": priority,
                    "generation_model": settings.gemini_model
                })

            logger.info(f"Successfully generated {len(test_cases)} test cases")

            return {
                "test_cases": test_cases,
                "prompt_used": prompt,
                "response_raw": response.text,
                "generation_metadata": {
                    "model": settings.gemini_model,
                    "test_type": test_type,
                    "requested_count": count,
                    "actual_count": len(test_cases),
                    "priority": priority
                }
            }

        except Exception as e:
            logger.error(f"Error generating test cases: {e}")
            return {
                "test_cases": [],
                "error": str(e),
                "generation_metadata": {
                    "model": settings.gemini_model,
                    "test_type": test_type,
                    "requested_count": count,
                    "actual_count": 0,
                    "priority": priority
                }
            }

    async def generate_mind_map_structure(
        self,
        test_cases: List[Dict[str, Any]],
        layout_type: str = "hierarchical",
        max_depth: int = 3
    ) -> Dict[str, Any]:
        """
        Generate mind map structure from test cases.

        Args:
            test_cases: List of test cases
            layout_type: Type of layout (hierarchical, radial, etc.)
            max_depth: Maximum depth of the mind map

        Returns:
            Dictionary containing mind map structure
        """
        try:
            # Construct the prompt for mind map generation
            prompt = self._build_mind_map_prompt(test_cases, layout_type, max_depth)

            # Generate content
            logger.info(f"Generating mind map structure for {len(test_cases)} test cases")

            response = await self._generate_content_async(prompt)

            # Parse the response
            mind_map_data = self._parse_mind_map_response(response.text)

            logger.info("Successfully generated mind map structure")

            return {
                "mind_map": mind_map_data,
                "prompt_used": prompt,
                "response_raw": response.text,
                "generation_metadata": {
                    "model": settings.gemini_model,
                    "layout_type": layout_type,
                    "max_depth": max_depth,
                    "test_case_count": len(test_cases)
                }
            }

        except Exception as e:
            logger.error(f"Error generating mind map: {e}")
            return {
                "mind_map": None,
                "error": str(e),
                "generation_metadata": {
                    "model": settings.gemini_model,
                    "layout_type": layout_type,
                    "max_depth": max_depth,
                    "test_case_count": len(test_cases)
                }
            }

    async def analyze_document_requirements(
        self,
        document_text: str,
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Analyze document to extract requirements and test points.

        Args:
            document_text: Text content of the document
            analysis_type: Type of analysis (comprehensive, quick, etc.)

        Returns:
            Dictionary containing analysis results
        """
        try:
            # Construct the prompt for document analysis
            prompt = self._build_analysis_prompt(document_text, analysis_type)

            # Generate content
            logger.info(f"Analyzing document with {len(document_text)} characters")

            response = await self._generate_content_async(prompt)

            # Parse the response
            analysis = self._parse_analysis_response(response.text)

            logger.info("Successfully analyzed document")

            return {
                "analysis": analysis,
                "prompt_used": prompt,
                "response_raw": response.text,
                "generation_metadata": {
                    "model": settings.gemini_model,
                    "analysis_type": analysis_type,
                    "document_length": len(document_text)
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing document: {e}")
            return {
                "analysis": None,
                "error": str(e),
                "generation_metadata": {
                    "model": settings.gemini_model,
                    "analysis_type": analysis_type,
                    "document_length": len(document_text)
                }
            }

    def _build_test_case_prompt(
        self,
        context: str,
        requirements: Optional[str],
        test_type: str,
        count: int,
        priority: str
    ) -> str:
        """Build prompt for test case generation."""
        prompt = f"""
Based on the following document context, please generate {count} {test_type} test cases with {priority} priority.

DOCUMENT CONTEXT:
{context}

"""
        if requirements:
            prompt += f"""
SPECIFIC REQUIREMENTS:
{requirements}

"""

        prompt += f"""
Please generate test cases in the following JSON format:
[
  {{
    "title": "Test case title",
    "description": "Detailed description of what is being tested",
    "preconditions": "Conditions that must be met before testing",
    "steps": [
      {{
        "step_number": 1,
        "action": "Action to perform",
        "expected_result": "Expected outcome"
      }}
    ],
    "expected_result": "Overall expected result",
    "priority": "{priority}",
    "category": "Category of the test",
    "tags": ["relevant", "tags"]
  }}
]

Requirements for test cases:
1. Each test case should be realistic and actionable
2. Steps should be clear and specific
3. Expected results should be measurable
4. Include proper error handling scenarios
5. Consider edge cases and boundary conditions
6. Ensure good coverage of the requirements
7. Default priority should be "{priority}"

Please respond with only the JSON array, no additional text.
"""
        return prompt

    def _build_mind_map_prompt(
        self,
        test_cases: List[Dict[str, Any]],
        layout_type: str,
        max_depth: int
    ) -> str:
        """Build prompt for mind map generation."""
        test_cases_text = json.dumps(test_cases, ensure_ascii=False, indent=2)

        prompt = f"""
Based on the following test cases, please generate a mind map structure in JSON format.

TEST CASES:
{test_cases_text}

Requirements for mind map:
1. Layout type: {layout_type}
2. Maximum depth: {max_depth}
3. Create a hierarchical structure that groups related test cases
4. Use meaningful categories for grouping
5. Include test case titles as leaf nodes
6. Provide node positions for visualization

Please generate a mind map in this JSON format:
{{
  "nodes": [
    {{
      "id": "unique_node_id",
      "label": "Node label",
      "type": "root|category|testcase",
      "x": 0,
      "y": 0,
      "color": "#color_code",
      "size": 20,
      "parent_id": "parent_node_id",
      "data": {{}}
    }}
  ],
  "edges": [
    {{
      "id": "unique_edge_id",
      "source": "source_node_id",
      "target": "target_node_id",
      "label": "relationship_label"
    }}
  ],
  "layout": {{
    "algorithm": "{layout_type}",
    "direction": "TB",
    "node_spacing": 100,
    "level_spacing": 150
  }}
}}

Please respond with only the JSON object, no additional text.
"""
        return prompt

    def _build_analysis_prompt(self, document_text: str, analysis_type: str) -> str:
        """Build prompt for document analysis."""
        # Truncate document if too long
        max_length = 8000
        truncated_text = document_text[:max_length]
        if len(document_text) > max_length:
            truncated_text += "...[document truncated]"

        prompt = f"""
Please analyze the following document and extract key information for test case generation.

DOCUMENT TEXT:
{truncated_text}

Please provide analysis in this JSON format:
{{
  "summary": "Brief summary of the document",
  "key_requirements": [
    "Key requirement 1",
    "Key requirement 2"
  ],
  "test_scenarios": [
    {{
      "scenario": "Test scenario description",
      "priority": "high|medium|low",
      "category": "functional|performance|security|usability"
    }}
  ],
  "entities": [
    {{
      "name": "Entity name",
      "type": "system|component|interface",
      "description": "Entity description"
    }}
  ],
  "risk_areas": [
    "Potential risk area 1",
    "Potential risk area 2"
  ],
  "test_types": [
    "Recommended test types"
  ]
}

Please respond with only the JSON object, no additional text.
"""
        return prompt

    async def _generate_content_async(self, prompt: str) -> Any:
        """Generate content using Gemini asynchronously."""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.model.generate_content(
                prompt,
                safety_settings=self.safety_settings
            )
        )
        return response

    def _parse_test_cases_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse test cases from Gemini response."""
        try:
            # Try to extract JSON from response
            response_text = response_text.strip()

            # Remove any markdown code blocks
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            test_cases = json.loads(response_text)

            # Validate and normalize test cases
            normalized_test_cases = []
            for i, test_case in enumerate(test_cases):
                normalized_case = {
                    "title": test_case.get("title", f"Test Case {i+1}"),
                    "description": test_case.get("description", ""),
                    "preconditions": test_case.get("preconditions", ""),
                    "steps": test_case.get("steps", []),
                    "expected_result": test_case.get("expected_result", ""),
                    "priority": test_case.get("priority", "medium"),
                    "category": test_case.get("category", "general"),
                    "tags": test_case.get("tags", [])
                }
                normalized_test_cases.append(normalized_case)

            return normalized_test_cases

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing test cases JSON: {e}")
            logger.error(f"Response text: {response_text[:500]}...")
            return []

    def _parse_mind_map_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse mind map structure from Gemini response."""
        try:
            response_text = response_text.strip()

            # Remove any markdown code blocks
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            mind_map = json.loads(response_text)
            return mind_map

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing mind map JSON: {e}")
            logger.error(f"Response text: {response_text[:500]}...")
            return None

    def _parse_analysis_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse analysis from Gemini response."""
        try:
            response_text = response_text.strip()

            # Remove any markdown code blocks
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            analysis = json.loads(response_text)
            return analysis

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing analysis JSON: {e}")
            logger.error(f"Response text: {response_text[:500]}...")
            return None

    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate Gemini API key format."""
        # Basic validation - Gemini API keys typically start with specific patterns
        return len(api_key) >= 30 and api_key.startswith(('AIza', 'GO'))

    @staticmethod
    def get_model_info() -> Dict[str, Any]:
        """Get information about available models."""
        return {
            "current_model": settings.gemini_model,
            "available_models": [
                "gemini-1.5-pro",
                "gemini-1.5-flash",
                "gemini-1.0-pro"
            ],
            "capabilities": [
                "text_generation",
                "structured_output",
                "test_case_generation",
                "document_analysis"
            ]
        }