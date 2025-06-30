import os
import json
from typing import List, Dict, Any, Optional

# ---------------------------------------------------------------------------
# Optional Cerebras SDK import
# ---------------------------------------------------------------------------
try:
    from cerebras.cloud.sdk import Cerebras  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    Cerebras = None  # Fallback for environments where SDK is not installed

from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.api_key = os.environ.get("CEREBRAS_API_KEY")
        if self.api_key and Cerebras is not None:
            self.client = Cerebras(api_key=self.api_key)
        else:
            self.client = None
            if not self.api_key:
                logger.warning("CEREBRAS_API_KEY not set - AI service will use fallback responses")
            elif Cerebras is None:
                logger.warning("cerebras-cloud-sdk not installed - AI service will use fallback responses")
        self.model = "llama-3.3-70b"
    
    def _make_completion(self, system_prompt: str, user_prompt: str, max_tokens: int = 8192) -> str:
        """Make a completion request to Cerebras API"""
        if not self.client:
            raise Exception("Cerebras client not initialized - API key missing")
            
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                stream=False,
                max_completion_tokens=max_tokens,
                temperature=0.1,
                top_p=1,
                seed=42
            )
            content = response.choices[0].message.content
            logger.info(f"AI Response received: {content[:200]}...")  # Log first 200 chars
            return content
        except Exception as e:
            logger.error(f"Error making AI completion: {str(e)}")
            raise Exception(f"AI service error: {str(e)}")

    def _extract_json_from_response(self, response: str) -> dict:
        """Extract JSON from AI response, handling cases where response contains extra text"""
        try:
            # First try to parse the entire response as JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # If that fails, try to find JSON within the response
            import re
            
            # Look for JSON array pattern
            json_array_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_array_match:
                try:
                    return json.loads(json_array_match.group())
                except json.JSONDecodeError:
                    pass
            
            # Look for JSON object pattern
            json_object_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_object_match:
                try:
                    return json.loads(json_object_match.group())
                except json.JSONDecodeError:
                    pass
            
            # If no valid JSON found, log the response and raise error
            logger.error(f"Could not extract valid JSON from response: {response}")
            raise json.JSONDecodeError("No valid JSON found in response", response, 0)

    def generate_action_plan_templates(self, issue_type: str, kpi_data: Dict, employee_data: List[Dict]) -> List[Dict]:
        """Generate AI-driven action plan templates based on identified issues"""
        
        system_prompt = """You are an expert HR consultant with deep knowledge of organizational psychology, employee engagement, and performance management.

        CRITICAL INSTRUCTION: You must respond with ONLY a valid JSON array. Do not include any explanatory text, markdown formatting, code blocks, or additional commentary before or after the JSON. Start your response with [ and end with ].

        Generate 3-4 practical action plan templates with clear steps, timelines, and success metrics."""

        user_prompt = f"""Generate action plan templates for: {issue_type}

Context: {json.dumps({"kpis": kpi_data, "employee_sample": employee_data[:3]}, indent=2)}

Return ONLY this JSON structure:
[
  {{
    "title": "Specific Action Plan Title",
    "description": "Clear 1-2 sentence description",
    "category": "engagement",
    "steps": [
      {{
        "step": "Specific actionable step",
        "timeline": "1-2 weeks",
        "responsible": "HR Team"
      }}
    ],
    "success_metrics": ["Engagement score increase", "Participation rate"],
    "estimated_duration": "4-6 weeks",
    "target_kpi": "Employee Engagement Score",
    "expected_improvement": "15-20%"
  }}
]"""

        try:
            response = self._make_completion(system_prompt, user_prompt, max_tokens=8192)
            # Parse JSON response using improved extraction
            action_plans = self._extract_json_from_response(response)
            
            # Ensure we have a list
            if isinstance(action_plans, dict):
                action_plans = [action_plans]
            elif not isinstance(action_plans, list):
                raise ValueError("Response is not a list or dict")
                
            return action_plans
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse AI response as JSON: {str(e)}")
            return self._get_fallback_action_plans(issue_type)
        except Exception as e:
            logger.error(f"Error generating action plans: {str(e)}")
            return self._get_fallback_action_plans(issue_type)

    def analyze_outliers(self, employee_data: List[Dict], kpi_thresholds: Dict) -> Dict:
        """Analyze employee data to identify outliers and provide insights"""
        
        system_prompt = """You are an expert data analyst specializing in HR analytics and employee behavior patterns.

        CRITICAL INSTRUCTION: You must respond with ONLY a valid JSON object. Do not include any explanatory text, markdown formatting, code blocks, or additional commentary before or after the JSON. Start your response with { and end with }.

        Analyze employee data to identify outliers and provide actionable insights."""

        user_prompt = f"""
        Analyze the following employee data to identify outliers and patterns:

        Employee Data: {json.dumps(employee_data, indent=2)}
        KPI Thresholds: {json.dumps(kpi_thresholds, indent=2)}

        Return a JSON object with this structure:
        {{
            "high_risk_employees": [
                {{
                    "employee_id": "ID",
                    "name": "Name",
                    "risk_factors": ["Factor 1", "Factor 2"],
                    "recommended_actions": ["Action 1", "Action 2"],
                    "priority_score": 0-100
                }}
            ],
            "medium_risk_employees": [...],
            "insights": [
                {{
                    "category": "engagement|performance|wellbeing",
                    "finding": "Key insight",
                    "recommendation": "Recommended action"
                }}
            ],
            "department_trends": {{
                "department_name": {{
                    "average_engagement": 0-100,
                    "trend": "improving|declining|stable",
                    "key_issues": ["Issue 1", "Issue 2"]
                }}
            }}
        }}
        """

        try:
            response = self._make_completion(system_prompt, user_prompt, max_tokens=8192)
            analysis = self._extract_json_from_response(response)
            return analysis
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse outlier analysis as JSON: {str(e)}")
            return self._get_fallback_outlier_analysis()
        except Exception as e:
            logger.error(f"Error analyzing outliers: {str(e)}")
            return self._get_fallback_outlier_analysis()

    def generate_survey_questions(self, kpi_focus: str, survey_type: str) -> List[Dict]:
        """Generate AI-optimized survey questions for specific KPIs"""
        
        system_prompt = """You are an expert in organizational psychology and survey design.

        CRITICAL INSTRUCTION: You must respond with ONLY a valid JSON array. Do not include any explanatory text, markdown formatting, code blocks, or additional commentary before or after the JSON. Start your response with [ and end with ].

        Create effective, unbiased survey questions that accurately measure specific KPIs."""

        user_prompt = f"""
        Generate 8-12 survey questions focused on measuring: {kpi_focus}
        Survey type: {survey_type}

        Return a JSON array with this structure:
        [
            {{
                "question": "Question text",
                "type": "likert|multiple_choice|text|rating",
                "options": ["Option 1", "Option 2"] or null for text,
                "kpi_mapping": "Which KPI this question measures",
                "weight": 0.1-1.0
            }}
        ]
        """

        try:
            response = self._make_completion(system_prompt, user_prompt, max_tokens=8192)
            questions = self._extract_json_from_response(response)
            
            # Ensure we have a list
            if isinstance(questions, dict):
                questions = [questions]
            elif not isinstance(questions, list):
                raise ValueError("Response is not a list or dict")
                
            return questions
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse survey questions as JSON: {str(e)}")
            return self._get_fallback_survey_questions(kpi_focus)
        except Exception as e:
            logger.error(f"Error generating survey questions: {str(e)}")
            return self._get_fallback_survey_questions(kpi_focus)

    def analyze_action_plan_efficacy(self, action_plan_data: Dict, before_metrics: Dict, after_metrics: Dict) -> Dict:
        """Analyze the efficacy of implemented action plans"""
        
        system_prompt = """You are an expert in HR analytics and organizational change management. Analyze the effectiveness of action plans by comparing before and after metrics.

        Provide:
        1. Quantitative efficacy scores
        2. Qualitative insights
        3. Recommendations for improvement
        4. Success factors identification"""

        user_prompt = f"""
        Analyze the efficacy of this action plan:

        Action Plan: {json.dumps(action_plan_data, indent=2)}
        Before Metrics: {json.dumps(before_metrics, indent=2)}
        After Metrics: {json.dumps(after_metrics, indent=2)}

        Return a JSON object with this structure:
        {{
            "efficacy_score": 0-100,
            "improvement_percentage": 0-100,
            "success_factors": ["Factor 1", "Factor 2"],
            "areas_for_improvement": ["Area 1", "Area 2"],
            "recommendations": [
                {{
                    "category": "process|content|timing|resources",
                    "recommendation": "Specific recommendation",
                    "priority": "high|medium|low"
                }}
            ],
            "kpi_impacts": {{
                "kpi_name": {{
                    "before": 0-100,
                    "after": 0-100,
                    "change": "+/-X%"
                }}
            }},
            "overall_assessment": "Detailed assessment text"
        }}
        """

        try:
            response = self._make_completion(system_prompt, user_prompt, max_tokens=8192)
            analysis = self._extract_json_from_response(response)
            return analysis
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse efficacy analysis as JSON: {str(e)}")
            return self._get_fallback_efficacy_analysis()
        except Exception as e:
            logger.error(f"Error analyzing action plan efficacy: {str(e)}")
            return self._get_fallback_efficacy_analysis()

    def generate_performance_insights(self, employee_data: Dict, performance_history: List[Dict]) -> Dict:
        """Generate AI-driven performance insights and recommendations"""
        
        system_prompt = """You are an expert performance management consultant. Analyze employee performance data to provide actionable insights for managers and HR teams.

        Focus on:
        1. Performance trends
        2. Strengths and development areas
        3. Career development opportunities
        4. Risk factors
        5. Personalized recommendations"""

        user_prompt = f"""
        Analyze performance data for this employee:

        Employee Data: {json.dumps(employee_data, indent=2)}
        Performance History: {json.dumps(performance_history, indent=2)}

        Return a JSON object with this structure:
        {{
            "performance_summary": {{
                "overall_rating": "exceeds|meets|below_expectations",
                "trend": "improving|stable|declining",
                "key_strengths": ["Strength 1", "Strength 2"],
                "development_areas": ["Area 1", "Area 2"]
            }},
            "recommendations": [
                {{
                    "category": "development|recognition|support|intervention",
                    "action": "Specific recommendation",
                    "timeline": "Timeline for action",
                    "expected_outcome": "Expected result"
                }}
            ],
            "career_development": {{
                "readiness_for_promotion": "ready|developing|not_ready",
                "suggested_roles": ["Role 1", "Role 2"],
                "skill_gaps": ["Skill 1", "Skill 2"],
                "development_plan": ["Action 1", "Action 2"]
            }},
            "risk_assessment": {{
                "flight_risk": "high|medium|low",
                "performance_risk": "high|medium|low",
                "mitigation_strategies": ["Strategy 1", "Strategy 2"]
            }}
        }}
        """

        try:
            response = self._make_completion(system_prompt, user_prompt, max_tokens=8192)
            insights = self._extract_json_from_response(response)
            return insights
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse performance insights as JSON: {str(e)}")
            return self._get_fallback_performance_insights()
        except Exception as e:
            logger.error(f"Error generating performance insights: {str(e)}")
            return self._get_fallback_performance_insights()

    # Fallback methods for when AI service fails
    def _get_fallback_action_plans(self, issue_type: str) -> List[Dict]:
        """Provide fallback action plans when AI service fails"""
        fallback_plans = {
            "low_engagement": [
                {
                    "title": "Team Building Workshop",
                    "description": "Organize team building activities to improve collaboration and engagement",
                    "category": "engagement",
                    "steps": [
                        {"step": "Plan team building activities", "timeline": "1 week", "responsible": "HR Team"},
                        {"step": "Execute workshop", "timeline": "1 day", "responsible": "External Facilitator"},
                        {"step": "Follow-up survey", "timeline": "2 weeks", "responsible": "HR Team"}
                    ],
                    "success_metrics": ["Engagement score improvement", "Team collaboration rating"],
                    "estimated_duration": "4 weeks",
                    "target_kpi": "Employee Engagement",
                    "expected_improvement": "15-20%"
                }
            ],
            "performance_issues": [
                {
                    "title": "Performance Improvement Plan",
                    "description": "Structured approach to address performance gaps",
                    "category": "performance",
                    "steps": [
                        {"step": "Identify performance gaps", "timeline": "1 week", "responsible": "Manager"},
                        {"step": "Create improvement plan", "timeline": "1 week", "responsible": "HR & Manager"},
                        {"step": "Regular check-ins", "timeline": "8 weeks", "responsible": "Manager"}
                    ],
                    "success_metrics": ["Performance rating improvement", "Goal achievement"],
                    "estimated_duration": "12 weeks",
                    "target_kpi": "Performance Rating",
                    "expected_improvement": "25-30%"
                }
            ]
        }
        return fallback_plans.get(issue_type, fallback_plans["low_engagement"])

    def _get_fallback_outlier_analysis(self) -> Dict:
        """Provide fallback outlier analysis"""
        return {
            "high_risk_employees": [],
            "medium_risk_employees": [],
            "insights": [
                {
                    "category": "engagement",
                    "finding": "AI analysis temporarily unavailable",
                    "recommendation": "Manual review recommended"
                }
            ],
            "department_trends": {}
        }

    def _get_fallback_survey_questions(self, kpi_focus: str) -> List[Dict]:
        """Provide fallback survey questions"""
        return [
            {
                "question": f"How would you rate your current level of {kpi_focus.lower()}?",
                "type": "likert",
                "options": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                "kpi_mapping": kpi_focus,
                "weight": 1.0
            }
        ]

    def _get_fallback_efficacy_analysis(self) -> Dict:
        """Provide fallback efficacy analysis"""
        return {
            "efficacy_score": 0,
            "improvement_percentage": 0,
            "success_factors": ["AI analysis temporarily unavailable"],
            "areas_for_improvement": ["Manual analysis recommended"],
            "recommendations": [],
            "kpi_impacts": {},
            "overall_assessment": "AI analysis service temporarily unavailable. Please conduct manual analysis."
        }

    def _get_fallback_performance_insights(self) -> Dict:
        """Provide fallback performance insights"""
        return {
            "performance_summary": {
                "overall_rating": "meets",
                "trend": "stable",
                "key_strengths": ["AI analysis unavailable"],
                "development_areas": ["Manual review needed"]
            },
            "recommendations": [],
            "career_development": {
                "readiness_for_promotion": "developing",
                "suggested_roles": [],
                "skill_gaps": [],
                "development_plan": []
            },
            "risk_assessment": {
                "flight_risk": "medium",
                "performance_risk": "medium",
                "mitigation_strategies": ["Manual assessment recommended"]
            }
        }

    def analyze_sentiment(self, text_list: List[str]) -> Dict[str, Any]:
        """Analyze sentiment of text responses"""
        if not self.client:
            return {
                "overall_sentiment": "neutral",
                "positive_percentage": 33.3,
                "neutral_percentage": 33.3,
                "negative_percentage": 33.3,
                "key_themes": ["communication", "work-life balance", "professional development"],
                "fallback_mode": True
            }
        
        system_prompt = """You are an expert HR analyst specializing in employee sentiment analysis.
        Analyze the provided employee feedback and return a JSON response with sentiment metrics."""
        
        user_prompt = f"""
        Analyze the sentiment of these employee responses:
        
        {json.dumps(text_list, indent=2)}
        
        Return a JSON object with:
        - overall_sentiment: "positive", "negative", or "neutral"
        - positive_percentage: percentage of positive responses
        - neutral_percentage: percentage of neutral responses  
        - negative_percentage: percentage of negative responses
        - key_themes: list of main themes/topics mentioned
        - concerns: list of main concerns raised
        - recommendations: suggested actions based on sentiment
        """
        
        try:
            response = self._make_completion(system_prompt, user_prompt)
            return self._extract_json_from_response(response)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse AI sentiment analysis response: {e}")
            return {
                "overall_sentiment": "neutral",
                "positive_percentage": 33.3,
                "neutral_percentage": 33.3,
                "negative_percentage": 33.3,
                "key_themes": ["communication", "work-life balance", "professional development"],
                "fallback_mode": True
            }

# Global AI service instance
ai_service = AIService() 