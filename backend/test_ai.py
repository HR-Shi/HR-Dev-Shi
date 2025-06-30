#!/usr/bin/env python3
"""
Test script for AI service improvements
"""
import os
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_json_extraction():
    """Test the JSON extraction functionality"""
    from ai_service import AIService
    
    # Create AI service instance (will use fallback if no API key)
    ai = AIService()
    
    # Test JSON extraction with various response formats
    test_cases = [
        # Valid JSON array
        '[{"title": "Test Plan", "category": "engagement"}]',
        
        # JSON with extra text
        'Here is the response:\n[{"title": "Test Plan", "category": "engagement"}]\nThat\'s the plan.',
        
        # JSON object instead of array
        '{"title": "Test Plan", "category": "engagement"}',
        
        # Markdown formatted JSON
        '```json\n[{"title": "Test Plan", "category": "engagement"}]\n```',
        
        # Invalid JSON
        'This is not JSON at all',
    ]
    
    for i, test_case in enumerate(test_cases):
        try:
            result = ai._extract_json_from_response(test_case)
            print(f"Test {i+1}: SUCCESS - {result}")
        except Exception as e:
            print(f"Test {i+1}: FAILED - {str(e)}")

def test_fallback_functionality():
    """Test that fallback methods work correctly"""
    from ai_service import AIService
    
    ai = AIService()
    
    # Test fallback action plans
    fallback_plans = ai._get_fallback_action_plans("low_engagement")
    print(f"Fallback action plans: {len(fallback_plans)} plans generated")
    
    # Test fallback outlier analysis
    fallback_analysis = ai._get_fallback_outlier_analysis()
    print(f"Fallback outlier analysis: {len(fallback_analysis['insights'])} insights")
    
    # Test fallback survey questions
    fallback_questions = ai._get_fallback_survey_questions("Employee Engagement")
    print(f"Fallback survey questions: {len(fallback_questions)} questions")

def test_ai_service_with_mock_data():
    """Test AI service methods with mock data (will use fallbacks if no API key)"""
    from ai_service import AIService
    
    ai = AIService()
    
    # Mock data
    kpi_data = {
        'kpis': [
            {'name': 'Employee Engagement', 'target_value': 80, 'current_value': 65, 'gap': 15}
        ]
    }
    
    employee_data = [
        {'department': 'Engineering', 'engagement_score': 70, 'status': 'Good'},
        {'department': 'Marketing', 'engagement_score': 60, 'status': 'Mid Concern'}
    ]
    
    try:
        # Test action plan generation
        plans = ai.generate_action_plan_templates('low_engagement', kpi_data, employee_data)
        print(f"Action plans generated: {len(plans)} plans")
        if plans:
            print(f"First plan: {plans[0]['title']}")
        
        # Test outlier analysis
        kpi_thresholds = {
            'Employee Engagement': {
                'target': 80,
                'current': 65,
                'threshold_low': 64,
                'threshold_high': 96
            }
        }
        
        analysis = ai.analyze_outliers(employee_data, kpi_thresholds)
        print(f"Outlier analysis: {len(analysis['insights'])} insights")
        
        # Test survey questions
        questions = ai.generate_survey_questions('Employee Engagement', 'pulse')
        print(f"Survey questions generated: {len(questions)} questions")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")

if __name__ == "__main__":
    print("Testing AI Service Improvements")
    print("=" * 40)
    
    # Check if API key is set
    api_key = os.environ.get("CEREBRAS_API_KEY")
    if api_key:
        print("✓ CEREBRAS_API_KEY is set")
    else:
        print("⚠ CEREBRAS_API_KEY not set - will use fallback responses")
    
    print("\n1. Testing JSON extraction...")
    test_json_extraction()
    
    print("\n2. Testing fallback functionality...")
    test_fallback_functionality()
    
    print("\n3. Testing AI service with mock data...")
    test_ai_service_with_mock_data()
    
    print("\n✓ All tests completed!") 