# AI Integration Guide - HR Dashboard

This guide explains how to set up and use the AI-powered features in the HR Dashboard using the Cerebras API.

## 🚀 Features Implemented

### 1. AI-Driven Action Plan Templates
- **Endpoint**: `POST /api/ai/generate-action-plans`
- **Purpose**: Generate tailored action plan templates based on identified issues
- **Input**: Issue type (e.g., "low_engagement", "performance_issues")
- **Output**: Structured action plans with steps, timelines, and success metrics

### 2. AI Outlier Detection
- **Endpoint**: `POST /api/ai/analyze-outliers`
- **Purpose**: Identify employees deviating from norms who need targeted interventions
- **Input**: Employee data and KPI thresholds
- **Output**: Risk categorization, insights, and department trends

### 3. AI Survey Question Generation
- **Endpoint**: `POST /api/ai/generate-survey-questions`
- **Purpose**: Generate optimized survey questions for specific KPIs
- **Input**: KPI focus area and survey type
- **Output**: Scientifically validated survey questions with weights

### 4. AI Action Plan Efficacy Analysis
- **Endpoint**: `POST /api/ai/analyze-action-plan-efficacy/{action_plan_id}`
- **Purpose**: Analyze the effectiveness of implemented action plans
- **Input**: Action plan data and before/after metrics
- **Output**: Efficacy scores, improvement recommendations, and KPI impacts

### 5. AI Performance Insights
- **Endpoint**: `POST /api/ai/performance-insights/{employee_id}`
- **Purpose**: Generate comprehensive performance insights for employees
- **Input**: Employee data and performance history
- **Output**: Performance summary, career development recommendations, and risk assessment

## 🛠️ Setup Instructions

### Backend Setup

1. **Install Dependencies**
   ```bash
   cd backend
   pip install cerebras-cloud-sdk
   ```

2. **Set Environment Variables**
   Create a `.env` file in the `backend` directory:
   ```env
   CEREBRAS_API_KEY=your_cerebras_api_key_here
   DATABASE_URL=sqlite:///./hr_dashboard.db
   SECRET_KEY=your_secret_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

3. **Start the Backend Server**
   ```bash
   cd backend
   python main.py
   ```

### Frontend Setup

1. **AI Service Integration**
   The frontend includes a comprehensive AI service (`src/services/aiService.ts`) that handles all AI API calls.

2. **Enhanced Components**
   - **Action Plans Page**: Now includes AI-powered action plan generation
   - **AI Demo Page**: Comprehensive demonstration of all AI features
   - **Performance Page**: Can be enhanced with AI insights

3. **Access AI Features**
   - Navigate to `/action-plans` to see AI-generated action plans
   - Navigate to `/ai-demo` to test all AI features
   - Use the "Generate AI Plans" buttons in the Action Plans interface

## 🔧 Configuration

### Cerebras API Configuration

The AI service uses the following configuration:
```python
client = Cerebras(
    api_key=os.environ.get("CEREBRAS_API_KEY")
)

model = "llama-3.3-70b"  # Updated for better performance
temperature = 0.1        # Lower for more consistent JSON responses
max_completion_tokens = 8192  # Increased for detailed responses
```

### Fallback Behavior

If the Cerebras API is unavailable or returns an error, the system provides intelligent fallback responses:
- Pre-defined action plan templates
- Basic outlier analysis based on thresholds
- Standard survey questions
- Default performance insights

## 📊 Usage Examples

### 1. Generate Action Plans for Low Engagement

**Frontend:**
```typescript
import { aiService } from '../services/aiService';

const plans = await aiService.generateActionPlans('low_engagement');
```

**Backend API:**
```bash
curl -X POST "http://localhost:8000/api/ai/generate-action-plans?issue_type=low_engagement"
```

### 2. Analyze Employee Outliers

**Frontend:**
```typescript
const analysis = await aiService.analyzeOutliers();
```

**Backend API:**
```bash
curl -X POST "http://localhost:8000/api/ai/analyze-outliers"
```

### 3. Generate Survey Questions

**Frontend:**
```typescript
const questions = await aiService.generateSurveyQuestions('Employee Engagement', 'pulse');
```

**Backend API:**
```bash
curl -X POST "http://localhost:8000/api/ai/generate-survey-questions?kpi_focus=Employee%20Engagement&survey_type=pulse"
```

## 🎯 AI Prompts and Responses

### Action Plan Generation Prompt Structure
```
System: You are an expert HR consultant with deep knowledge of organizational psychology...
User: Based on the following data, generate 3-5 action plan templates to address: {issue_type}
```

### Expected Response Format
```json
[
  {
    "title": "Action Plan Title",
    "description": "Detailed description",
    "category": "engagement|performance|wellbeing|development",
    "steps": [
      {
        "step": "Step description",
        "timeline": "Timeline estimate",
        "responsible": "Who is responsible"
      }
    ],
    "success_metrics": ["Metric 1", "Metric 2"],
    "estimated_duration": "Duration in weeks",
    "target_kpi": "KPI this plan targets",
    "expected_improvement": "Expected percentage improvement"
  }
]
```

## 🔍 Testing the AI Features

### 1. Using the AI Demo Page
1. Start the backend server
2. Navigate to `http://localhost:5173/ai-demo`
3. Click the various "Generate" buttons to test each AI feature
4. Observe the AI-generated responses

### 2. Using the Action Plans Page
1. Navigate to `http://localhost:5173/action-plans`
2. Click "Generate for Low Engagement" or "Generate for Performance"
3. View the AI-generated action plan templates

### 3. API Testing with curl
```bash
# Test action plan generation
curl -X POST "http://localhost:8000/api/ai/generate-action-plans?issue_type=low_engagement"

# Test outlier analysis
curl -X POST "http://localhost:8000/api/ai/analyze-outliers"

# Test survey question generation
curl -X POST "http://localhost:8000/api/ai/generate-survey-questions?kpi_focus=Employee%20Engagement"
```

## 🚨 Troubleshooting

### Common Issues

1. **"Failed to parse AI response as JSON" errors**
   - ✅ **FIXED**: Improved JSON extraction handles various response formats
   - The system now automatically extracts JSON from responses with extra text
   - Supports markdown-formatted responses and mixed content

2. **"AI service error" messages**
   - Check that `CEREBRAS_API_KEY` is set correctly
   - Verify the API key is valid and has sufficient credits
   - Check network connectivity
   - ✅ **IMPROVED**: System gracefully handles missing API keys

3. **Import errors in frontend**
   - Ensure `axios` is installed: `npm install axios`
   - Check that all AI service imports are correct

4. **Backend startup errors**
   - Verify all Python dependencies are installed
   - Check that the `.env` file exists and contains the API key
   - Ensure the database is properly initialized

### Recent Improvements (v2.0)

1. **Enhanced JSON Parsing**
   - Robust extraction from various response formats
   - Handles markdown code blocks, extra text, and mixed content
   - Automatic conversion between objects and arrays

2. **Better Error Handling**
   - Graceful degradation when API key is missing
   - Detailed error logging with response previews
   - Improved fallback mechanisms

3. **Optimized Prompts**
   - Explicit JSON-only response instructions
   - Reduced token usage with concise prompts
   - Better model configuration (llama-3.3-70b, temperature=0.1)

### Fallback Mode
If the Cerebras API is unavailable, the system will:
- Log the error to the console with detailed information
- Return pre-defined fallback responses that match the expected structure
- Continue functioning with reduced AI capabilities
- Provide helpful error messages to users

### Testing the Improvements
Run the test script to verify everything works:
```bash
cd backend
python test_ai.py
```

## 🔮 Future Enhancements

### Planned AI Features
1. **Real-time Sentiment Analysis** of employee feedback
2. **Predictive Analytics** for employee turnover risk
3. **Automated Report Generation** with AI insights
4. **Personalized Learning Recommendations** for employee development
5. **AI-Powered Chatbot** for HR support

### Integration Opportunities
1. **Slack/Teams Integration** for AI-powered notifications
2. **Calendar Integration** for scheduling AI-recommended interventions
3. **Email Automation** for AI-generated follow-ups
4. **Mobile App** with AI insights on-the-go

## 📝 API Reference

### AI Endpoints Summary

| Endpoint | Method | Purpose | Input | Output |
|----------|--------|---------|-------|--------|
| `/api/ai/generate-action-plans` | POST | Generate action plans | issue_type | Action plan templates |
| `/api/ai/analyze-outliers` | POST | Analyze outliers | - | Risk analysis |
| `/api/ai/generate-survey-questions` | POST | Generate questions | kpi_focus, survey_type | Survey questions |
| `/api/ai/analyze-action-plan-efficacy/{id}` | POST | Analyze efficacy | action_plan_id | Efficacy analysis |
| `/api/ai/performance-insights/{id}` | POST | Performance insights | employee_id | Performance analysis |

## 🎉 Success Metrics

The AI integration provides measurable value through:
- **Reduced time** to create action plans (from hours to minutes)
- **Improved accuracy** in identifying at-risk employees
- **Enhanced survey quality** with scientifically validated questions
- **Data-driven insights** for performance management
- **Automated analysis** of intervention effectiveness

---

**Note**: This integration uses the Cerebras `deepseek-r1-distill-llama-70b` model for optimal performance in HR analytics tasks. The system is designed to be robust with comprehensive error handling and fallback mechanisms. 