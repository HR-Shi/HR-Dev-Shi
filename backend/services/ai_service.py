import json

class AIService:
    async def analyze_employee_risk_factors(self, rating_data: dict) -> dict:
        """Analyze employee risk factors based on parameter ratings"""
        try:
            prompt = f"""
            Analyze the following employee parameter ratings and identify potential risk factors:
            
            Employee: {rating_data['employee_name']} - {rating_data['position']}
            
            Parameter Ratings:
            {json.dumps(rating_data['ratings'], indent=2)}
            
            Provide a comprehensive risk assessment covering:
            1. High-risk areas (parameters with ratings below 3.0)
            2. Burnout indicators (especially ETH_34, PER_23, SOC_15)
            3. Performance concerns (PER category parameters)
            4. Leadership risks (if applicable)
            5. Recommended immediate interventions
            6. Long-term development needs
            
            Format as JSON with confidence_score (0.0-1.0).
            """
            
            response = await self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500
            )
            
            result = json.loads(response.choices[0].message.content)
            result["model_version"] = "cerebras-llama-3.3-70B"
            result["analysis_type"] = "risk_assessment"
            
            return result
            
        except Exception as e:
            return {
                "error": f"Risk analysis failed: {str(e)}",
                "confidence_score": 0.0,
                "risk_level": "unknown"
            }

    async def predict_leadership_potential(self, rating_data: dict) -> dict:
        """Predict leadership potential based on parameter ratings"""
        try:
            prompt = f"""
            Analyze the following employee parameter ratings to predict leadership potential:
            
            Employee: {rating_data['employee_name']} - {rating_data['position']}
            
            Parameter Ratings:
            {json.dumps(rating_data['ratings'], indent=2)}
            
            Focus on leadership-relevant parameters:
            - PER_19 (Learning Agility)
            - COG_32 (Strategic Mindset) 
            - PER_24 (Leadership)
            - COG_03 (Growth Mindset)
            - PER_18 (Adaptability)
            - SOC_17 (Communication Skills)
            - ETH_25 (Integrity)
            
            Provide assessment covering:
            1. Current leadership readiness (1-5 scale)
            2. Key leadership strengths
            3. Areas needing development
            4. Recommended leadership track
            5. Timeline for leadership roles
            6. Specific development actions
            
            Format as JSON with confidence_score (0.0-1.0).
            """
            
            response = await self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500
            )
            
            result = json.loads(response.choices[0].message.content)
            result["model_version"] = "cerebras-llama-3.3-70B"
            result["analysis_type"] = "leadership_potential"
            
            return result
            
        except Exception as e:
            return {
                "error": f"Leadership prediction failed: {str(e)}",
                "confidence_score": 0.0,
                "leadership_readiness": 0.0
            }

    async def generate_development_recommendations(self, rating_data: dict) -> dict:
        """Generate personalized development recommendations"""
        try:
            prompt = f"""
            Create personalized development recommendations based on these parameter ratings:
            
            Employee: {rating_data['employee_name']} - {rating_data['position']}
            
            Parameter Ratings:
            {json.dumps(rating_data['ratings'], indent=2)}
            
            Provide comprehensive development plan including:
            1. Top 3 priority development areas
            2. Specific learning objectives for each area
            3. Recommended training programs/resources
            4. Mentoring/coaching suggestions
            5. Stretch assignments aligned with growth areas
            6. Timeline and milestones (3, 6, 12 months)
            7. Success metrics for each recommendation
            
            Consider the employee's current role and potential career progression.
            
            Format as JSON with confidence_score (0.0-1.0) and actionable recommendations.
            """
            
            response = await self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=2000
            )
            
            result = json.loads(response.choices[0].message.content)
            result["model_version"] = "cerebras-llama-3.3-70B"
            result["analysis_type"] = "development_recommendations"
            
            return result
            
        except Exception as e:
            return {
                "error": f"Development recommendations failed: {str(e)}",
                "confidence_score": 0.0,
                "recommendations": []
            } 