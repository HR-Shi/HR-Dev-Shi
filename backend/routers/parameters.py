from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from uuid import UUID
import uuid
from services.database import get_db_connection
from services.ai_service import AIService
from auth.dependencies import get_current_user
import json

router = APIRouter(prefix="/parameters", tags=["Employee Parameters"])

# Pydantic Models
class ParameterDefinition(BaseModel):
    parameter_id: str
    name: str
    category: str
    definition: str
    relevance_summary: str
    behavioral_anchors: Dict[str, Any]
    is_active: bool = True

class ParameterRating(BaseModel):
    employee_id: UUID
    parameter_id: str
    rating_value: float = Field(ge=1.0, le=5.0)
    rater_id: Optional[UUID] = None
    rater_type: str = Field(..., pattern="^(self|manager|peer|system)$")
    evidence_text: Optional[str] = None
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    rating_period_start: date
    rating_period_end: date
    review_cycle_id: Optional[UUID] = None

class ParameterRatingResponse(BaseModel):
    id: UUID
    employee_id: UUID
    employee_name: str
    parameter_id: str
    parameter_name: str
    rating_value: float
    rater_type: str
    evidence_text: Optional[str]
    confidence_score: float
    rating_period_start: date
    rating_period_end: date
    created_at: datetime

class AdvancedKPI(BaseModel):
    kpi_code: str
    name: str
    description: str
    formula_expression: str
    parameter_weights: Dict[str, float]
    target_value: Optional[float] = None
    calculation_frequency: str = "quarterly"

class KPICalculationResult(BaseModel):
    employee_id: UUID
    employee_name: str
    kpi_code: str
    kpi_name: str
    calculated_value: float
    component_scores: Dict[str, float]
    calculation_date: datetime
    period_start: date
    period_end: date
    confidence_score: float

class FeedbackRequest(BaseModel):
    employee_id: UUID
    request_type: str = Field(..., pattern="^(360|peer|upward|self)$")
    parameters_to_rate: List[str]
    target_raters: List[UUID]
    due_date: date
    instructions: Optional[str] = None

class BulkParameterRating(BaseModel):
    ratings: List[ParameterRating]

# Initialize AI Service
ai_service = AIService()

@router.get("/definitions", response_model=List[ParameterDefinition])
async def get_parameter_definitions(
    category: Optional[str] = Query(None, description="Filter by category"),
    is_active: bool = Query(True, description="Filter by active status"),
    db=Depends(get_db_connection)
):
    """Get all parameter definitions with optional filtering"""
    try:
        query = """
            SELECT parameter_id, name, category, definition, relevance_summary, 
                   behavioral_anchors, is_active
            FROM evaluation_parameters 
            WHERE 1=1
        """
        params = []
        
        if category:
            query += " AND category = %s"
            params.append(category)
            
        if is_active is not None:
            query += " AND is_active = %s"
            params.append(is_active)
            
        query += " ORDER BY category, parameter_id"
        
        result = await db.fetch(query, *params)
        
        return [
            ParameterDefinition(
                parameter_id=row['parameter_id'],
                name=row['name'],
                category=row['category'],
                definition=row['definition'],
                relevance_summary=row['relevance_summary'],
                behavioral_anchors=row['behavioral_anchors'],
                is_active=row['is_active']
            )
            for row in result
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch parameter definitions: {str(e)}")

@router.get("/categories")
async def get_parameter_categories(db=Depends(get_db_connection)):
    """Get all parameter categories with counts"""
    try:
        result = await db.fetch("""
            SELECT category, 
                   COUNT(*) as parameter_count,
                   COUNT(CASE WHEN is_active THEN 1 END) as active_count
            FROM evaluation_parameters 
            GROUP BY category
            ORDER BY category
        """)
        
        return [
            {
                "category": row['category'],
                "parameter_count": row['parameter_count'],
                "active_count": row['active_count']
            }
            for row in result
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch categories: {str(e)}")

@router.post("/ratings", response_model=Dict[str, str])
async def create_parameter_rating(
    rating: ParameterRating,
    current_user=Depends(get_current_user),
    db=Depends(get_db_connection)
):
    """Create a new parameter rating for an employee"""
    try:
        # Verify parameter exists
        param_check = await db.fetchrow(
            "SELECT parameter_id FROM evaluation_parameters WHERE parameter_id = %s AND is_active = true",
            rating.parameter_id
        )
        if not param_check:
            raise HTTPException(status_code=404, detail=f"Parameter {rating.parameter_id} not found or inactive")
        
        # Verify employee exists
        emp_check = await db.fetchrow(
            "SELECT id FROM employees WHERE id = %s AND is_active = true",
            rating.employee_id
        )
        if not emp_check:
            raise HTTPException(status_code=404, detail="Employee not found or inactive")
        
        rating_id = uuid.uuid4()
        await db.execute("""
            INSERT INTO employee_parameter_ratings 
            (id, employee_id, parameter_id, rating_value, rater_id, rater_type, 
             evidence_text, confidence_score, rating_period_start, rating_period_end, review_cycle_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, 
        rating_id, rating.employee_id, rating.parameter_id, rating.rating_value,
        rating.rater_id or current_user.id, rating.rater_type, rating.evidence_text,
        rating.confidence_score, rating.rating_period_start, rating.rating_period_end,
        rating.review_cycle_id)
        
        return {"message": "Parameter rating created successfully", "rating_id": str(rating_id)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create rating: {str(e)}")

@router.post("/ratings/bulk", response_model=Dict[str, Any])
async def create_bulk_parameter_ratings(
    bulk_ratings: BulkParameterRating,
    current_user=Depends(get_current_user),
    db=Depends(get_db_connection)
):
    """Create multiple parameter ratings in bulk"""
    try:
        created_ratings = []
        failed_ratings = []
        
        for rating in bulk_ratings.ratings:
            try:
                # Verify parameter and employee exist
                param_check = await db.fetchrow(
                    "SELECT parameter_id FROM evaluation_parameters WHERE parameter_id = %s AND is_active = true",
                    rating.parameter_id
                )
                emp_check = await db.fetchrow(
                    "SELECT id FROM employees WHERE id = %s AND is_active = true",
                    rating.employee_id
                )
                
                if not param_check or not emp_check:
                    failed_ratings.append({
                        "employee_id": str(rating.employee_id),
                        "parameter_id": rating.parameter_id,
                        "error": "Employee or parameter not found"
                    })
                    continue
                
                rating_id = uuid.uuid4()
                await db.execute("""
                    INSERT INTO employee_parameter_ratings 
                    (id, employee_id, parameter_id, rating_value, rater_id, rater_type, 
                     evidence_text, confidence_score, rating_period_start, rating_period_end, review_cycle_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, 
                rating_id, rating.employee_id, rating.parameter_id, rating.rating_value,
                rating.rater_id or current_user.id, rating.rater_type, rating.evidence_text,
                rating.confidence_score, rating.rating_period_start, rating.rating_period_end,
                rating.review_cycle_id)
                
                created_ratings.append(str(rating_id))
                
            except Exception as e:
                failed_ratings.append({
                    "employee_id": str(rating.employee_id),
                    "parameter_id": rating.parameter_id,
                    "error": str(e)
                })
        
        return {
            "created_count": len(created_ratings),
            "failed_count": len(failed_ratings),
            "created_ratings": created_ratings,
            "failed_ratings": failed_ratings
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create bulk ratings: {str(e)}")

@router.get("/employees/{employee_id}/ratings", response_model=List[ParameterRatingResponse])
async def get_employee_parameter_ratings(
    employee_id: UUID,
    parameter_id: Optional[str] = Query(None, description="Filter by parameter"),
    rater_type: Optional[str] = Query(None, description="Filter by rater type"),
    period_start: Optional[date] = Query(None, description="Filter by period start"),
    period_end: Optional[date] = Query(None, description="Filter by period end"),
    latest_only: bool = Query(False, description="Get only latest ratings per parameter"),
    db=Depends(get_db_connection)
):
    """Get parameter ratings for a specific employee"""
    try:
        base_query = """
            SELECT epr.id, epr.employee_id, e.name as employee_name,
                   epr.parameter_id, ep.name as parameter_name,
                   epr.rating_value, epr.rater_type, epr.evidence_text,
                   epr.confidence_score, epr.rating_period_start, epr.rating_period_end,
                   epr.created_at
            FROM employee_parameter_ratings epr
            JOIN employees e ON epr.employee_id = e.id
            JOIN evaluation_parameters ep ON epr.parameter_id = ep.parameter_id
            WHERE epr.employee_id = %s
        """
        
        params = [employee_id]
        
        if parameter_id:
            base_query += " AND epr.parameter_id = %s"
            params.append(parameter_id)
            
        if rater_type:
            base_query += " AND epr.rater_type = %s"
            params.append(rater_type)
            
        if period_start:
            base_query += " AND epr.rating_period_start >= %s"
            params.append(period_start)
            
        if period_end:
            base_query += " AND epr.rating_period_end <= %s"
            params.append(period_end)
        
        if latest_only:
            # Get only the latest rating for each parameter
            query = f"""
                SELECT DISTINCT ON (parameter_id) *
                FROM ({base_query}) subq
                ORDER BY parameter_id, rating_period_end DESC, created_at DESC
            """
        else:
            query = base_query + " ORDER BY epr.rating_period_end DESC, epr.created_at DESC"
        
        result = await db.fetch(query, *params)
        
        return [
            ParameterRatingResponse(
                id=row['id'],
                employee_id=row['employee_id'],
                employee_name=row['employee_name'],
                parameter_id=row['parameter_id'],
                parameter_name=row['parameter_name'],
                rating_value=row['rating_value'],
                rater_type=row['rater_type'],
                evidence_text=row['evidence_text'],
                confidence_score=row['confidence_score'],
                rating_period_start=row['rating_period_start'],
                rating_period_end=row['rating_period_end'],
                created_at=row['created_at']
            )
            for row in result
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch employee ratings: {str(e)}")

@router.get("/kpis/definitions", response_model=List[AdvancedKPI])
async def get_advanced_kpi_definitions(db=Depends(get_db_connection)):
    """Get all advanced KPI definitions"""
    try:
        result = await db.fetch("""
            SELECT kpi_code, name, description, formula_expression, 
                   parameter_weights, target_value, calculation_frequency
            FROM advanced_kpis 
            WHERE is_active = true
            ORDER BY kpi_code
        """)
        
        return [
            AdvancedKPI(
                kpi_code=row['kpi_code'],
                name=row['name'],
                description=row['description'],
                formula_expression=row['formula_expression'],
                parameter_weights=row['parameter_weights'],
                target_value=row['target_value'],
                calculation_frequency=row['calculation_frequency']
            )
            for row in result
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch KPI definitions: {str(e)}")

@router.post("/kpis/calculate/{employee_id}/{kpi_code}", response_model=KPICalculationResult)
async def calculate_employee_kpi(
    employee_id: UUID,
    kpi_code: str,
    period_start: Optional[date] = Query(None, description="Calculation period start"),
    period_end: Optional[date] = Query(None, description="Calculation period end"),
    db=Depends(get_db_connection)
):
    """Calculate a specific KPI for an employee"""
    try:
        # Set default period if not provided
        if not period_start:
            period_start = date.today().replace(day=1)  # First day of current month
        if not period_end:
            period_end = date.today()
        
        # Call the database function to calculate KPI
        result = await db.fetchrow(
            "SELECT calculate_advanced_kpi(%s, %s, %s, %s) as calculated_value",
            employee_id, kpi_code, period_start, period_end
        )
        
        if result is None:
            raise HTTPException(status_code=404, detail="KPI calculation failed")
        
        # Get the stored calculation result
        kpi_result = await db.fetchrow("""
            SELECT eakv.employee_id, e.name as employee_name, eakv.kpi_code, 
                   ak.name as kpi_name, eakv.calculated_value, eakv.component_scores,
                   eakv.calculation_date, eakv.period_start, eakv.period_end, eakv.confidence_score
            FROM employee_advanced_kpi_values eakv
            JOIN employees e ON eakv.employee_id = e.id
            JOIN advanced_kpis ak ON eakv.kpi_code = ak.kpi_code
            WHERE eakv.employee_id = %s AND eakv.kpi_code = %s AND eakv.period_start = %s
            ORDER BY eakv.calculation_date DESC
            LIMIT 1
        """, employee_id, kpi_code, period_start)
        
        if not kpi_result:
            raise HTTPException(status_code=404, detail="KPI calculation result not found")
        
        return KPICalculationResult(
            employee_id=kpi_result['employee_id'],
            employee_name=kpi_result['employee_name'],
            kpi_code=kpi_result['kpi_code'],
            kpi_name=kpi_result['kpi_name'],
            calculated_value=float(kpi_result['calculated_value']),
            component_scores=kpi_result['component_scores'],
            calculation_date=kpi_result['calculation_date'],
            period_start=kpi_result['period_start'],
            period_end=kpi_result['period_end'],
            confidence_score=float(kpi_result['confidence_score'])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate KPI: {str(e)}")

@router.post("/kpis/calculate/bulk", response_model=Dict[str, Any])
async def calculate_all_kpis(
    period_start: Optional[date] = Query(None, description="Calculation period start"),
    period_end: Optional[date] = Query(None, description="Calculation period end"),
    db=Depends(get_db_connection)
):
    """Calculate all KPIs for all employees"""
    try:
        # Set default period if not provided
        if not period_start:
            period_start = date.today().replace(day=1)  # First day of current month
        if not period_end:
            period_end = date.today()
        
        # Call the database function to recalculate all KPIs
        result = await db.fetchrow(
            "SELECT recalculate_all_advanced_kpis(%s, %s) as status",
            period_start, period_end
        )
        
        return {
            "message": "KPI calculations completed",
            "status": result['status'],
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate KPIs: {str(e)}")

@router.get("/kpis/employees/{employee_id}", response_model=List[KPICalculationResult])
async def get_employee_kpi_values(
    employee_id: UUID,
    kpi_code: Optional[str] = Query(None, description="Filter by KPI code"),
    limit: int = Query(10, description="Number of results to return"),
    db=Depends(get_db_connection)
):
    """Get KPI calculation results for an employee"""
    try:
        query = """
            SELECT eakv.employee_id, e.name as employee_name, eakv.kpi_code, 
                   ak.name as kpi_name, eakv.calculated_value, eakv.component_scores,
                   eakv.calculation_date, eakv.period_start, eakv.period_end, eakv.confidence_score
            FROM employee_advanced_kpi_values eakv
            JOIN employees e ON eakv.employee_id = e.id
            JOIN advanced_kpis ak ON eakv.kpi_code = ak.kpi_code
            WHERE eakv.employee_id = %s
        """
        
        params = [employee_id]
        
        if kpi_code:
            query += " AND eakv.kpi_code = %s"
            params.append(kpi_code)
        
        query += " ORDER BY eakv.calculation_date DESC LIMIT %s"
        params.append(limit)
        
        result = await db.fetch(query, *params)
        
        return [
            KPICalculationResult(
                employee_id=row['employee_id'],
                employee_name=row['employee_name'],
                kpi_code=row['kpi_code'],
                kpi_name=row['kpi_name'],
                calculated_value=float(row['calculated_value']),
                component_scores=row['component_scores'],
                calculation_date=row['calculation_date'],
                period_start=row['period_start'],
                period_end=row['period_end'],
                confidence_score=float(row['confidence_score'])
            )
            for row in result
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch KPI values: {str(e)}")

@router.post("/feedback/request", response_model=Dict[str, str])
async def create_feedback_request(
    request: FeedbackRequest,
    current_user=Depends(get_current_user),
    db=Depends(get_db_connection)
):
    """Create a 360-degree feedback request"""
    try:
        request_id = uuid.uuid4()
        
        await db.execute("""
            INSERT INTO feedback_requests 
            (id, employee_id, requested_by, request_type, parameters_to_rate, 
             target_raters, due_date, instructions)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, 
        request_id, request.employee_id, current_user.id, request.request_type,
        request.parameters_to_rate, [str(r) for r in request.target_raters],
        request.due_date, request.instructions)
        
        return {"message": "Feedback request created successfully", "request_id": str(request_id)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create feedback request: {str(e)}")

@router.post("/ai/generate-evaluation-insights/{employee_id}")
async def generate_ai_evaluation_insights(
    employee_id: UUID,
    insight_type: str = Query(..., description="Type of insight: risk_assessment, potential_prediction, development_recommendation"),
    db=Depends(get_db_connection)
):
    """Generate AI-powered insights based on employee parameter ratings"""
    try:
        # Get employee parameter ratings
        ratings = await db.fetch("""
            SELECT epr.parameter_id, ep.name, ep.category, epr.rating_value, 
                   epr.rater_type, epr.evidence_text, epr.confidence_score
            FROM employee_parameter_ratings epr
            JOIN evaluation_parameters ep ON epr.parameter_id = ep.parameter_id
            WHERE epr.employee_id = %s
            ORDER BY epr.rating_period_end DESC, epr.created_at DESC
        """, employee_id)
        
        if not ratings:
            raise HTTPException(status_code=404, detail="No parameter ratings found for employee")
        
        # Get employee info
        employee = await db.fetchrow(
            "SELECT name, position, department_id FROM employees WHERE id = %s",
            employee_id
        )
        
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Prepare data for AI analysis
        rating_data = {
            "employee_name": employee['name'],
            "position": employee['position'],
            "ratings": [
                {
                    "parameter_id": r['parameter_id'],
                    "parameter_name": r['name'],
                    "category": r['category'],
                    "rating": float(r['rating_value']),
                    "rater_type": r['rater_type'],
                    "evidence": r['evidence_text'],
                    "confidence": float(r['confidence_score'])
                }
                for r in ratings
            ]
        }
        
        # Generate AI insights based on type
        if insight_type == "risk_assessment":
            insights = await ai_service.analyze_employee_risk_factors(rating_data)
        elif insight_type == "potential_prediction":
            insights = await ai_service.predict_leadership_potential(rating_data)
        elif insight_type == "development_recommendation":
            insights = await ai_service.generate_development_recommendations(rating_data)
        else:
            raise HTTPException(status_code=400, detail="Invalid insight type")
        
        # Store insights in database
        insight_id = uuid.uuid4()
        await db.execute("""
            INSERT INTO employee_ai_insights 
            (id, employee_id, insight_type, insight_data, confidence_score, model_version, is_actionable)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, 
        insight_id, employee_id, insight_type, json.dumps(insights),
        insights.get('confidence_score', 0.8), "cerebras-llama-3.3-70B", True)
        
        return {
            "insight_id": str(insight_id),
            "employee_id": str(employee_id),
            "insight_type": insight_type,
            "insights": insights,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate AI insights: {str(e)}")

@router.get("/analytics/department-comparison")
async def get_department_parameter_comparison(
    parameter_id: Optional[str] = Query(None, description="Specific parameter to analyze"),
    category: Optional[str] = Query(None, description="Parameter category to analyze"),
    db=Depends(get_db_connection)
):
    """Get department-level parameter comparison analytics"""
    try:
        base_query = """
            SELECT d.name as department_name, ep.parameter_id, ep.name as parameter_name,
                   ep.category, AVG(epr.rating_value) as avg_rating,
                   COUNT(epr.id) as rating_count, AVG(epr.confidence_score) as avg_confidence,
                   STDDEV(epr.rating_value) as rating_stddev
            FROM departments d
            JOIN employees e ON d.id = e.department_id
            JOIN employee_parameter_ratings epr ON e.id = epr.employee_id
            JOIN evaluation_parameters ep ON epr.parameter_id = ep.parameter_id
            WHERE e.is_active = true AND ep.is_active = true
        """
        
        params = []
        
        if parameter_id:
            base_query += " AND ep.parameter_id = %s"
            params.append(parameter_id)
            
        if category:
            base_query += " AND ep.category = %s"
            params.append(category)
        
        base_query += """
            GROUP BY d.name, ep.parameter_id, ep.name, ep.category
            ORDER BY d.name, ep.category, ep.parameter_id
        """
        
        result = await db.fetch(base_query, *params)
        
        # Organize by department
        departments = {}
        for row in result:
            dept_name = row['department_name']
            if dept_name not in departments:
                departments[dept_name] = []
            
            departments[dept_name].append({
                "parameter_id": row['parameter_id'],
                "parameter_name": row['parameter_name'],
                "category": row['category'],
                "average_rating": float(row['avg_rating']) if row['avg_rating'] else 0.0,
                "rating_count": row['rating_count'],
                "average_confidence": float(row['avg_confidence']) if row['avg_confidence'] else 0.0,
                "rating_variance": float(row['rating_stddev']) if row['rating_stddev'] else 0.0
            })
        
        return {
            "departments": departments,
            "total_departments": len(departments),
            "analysis_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch department comparison: {str(e)}")

@router.get("/health")
async def parameter_system_health(db=Depends(get_db_connection)):
    """Get health status of the parameter system"""
    try:
        # Count parameters by category
        param_counts = await db.fetch("""
            SELECT category, COUNT(*) as count, COUNT(CASE WHEN is_active THEN 1 END) as active_count
            FROM evaluation_parameters
            GROUP BY category
        """)
        
        # Count recent ratings
        recent_ratings = await db.fetchval("""
            SELECT COUNT(*) FROM employee_parameter_ratings 
            WHERE created_at > NOW() - INTERVAL '30 days'
        """)
        
        # Count employees with ratings
        employees_with_ratings = await db.fetchval("""
            SELECT COUNT(DISTINCT employee_id) FROM employee_parameter_ratings
        """)
        
        # Count KPI calculations
        recent_kpi_calcs = await db.fetchval("""
            SELECT COUNT(*) FROM employee_advanced_kpi_values 
            WHERE calculation_date > NOW() - INTERVAL '30 days'
        """)
        
        return {
            "status": "healthy",
            "parameter_categories": {row['category']: {"total": row['count'], "active": row['active_count']} for row in param_counts},
            "recent_ratings_30d": recent_ratings,
            "employees_with_ratings": employees_with_ratings,
            "recent_kpi_calculations_30d": recent_kpi_calcs,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system health: {str(e)}") 