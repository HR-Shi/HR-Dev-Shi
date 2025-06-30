#!/usr/bin/env python3
"""
COMPREHENSIVE SYNTHETIC DATA GENERATOR
35-Parameter Employee Evaluation System
Generates high-quality, realistic data for HR Dashboard
"""

import asyncio
import asyncpg
import random
import json
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from faker import Faker
import uuid
import numpy as np
from dataclasses import dataclass
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

fake = Faker()

@dataclass
class Employee:
    id: str
    name: str
    email: str
    position: str
    department_id: str
    hire_date: date
    manager_id: str = None

@dataclass
class Department:
    id: str
    name: str
    manager_id: str = None

class SyntheticDataGenerator:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        if not self.db_url:
            self.db_url = "postgresql://postgres.udaulvygaczcsrgybdqw:6wjSo5aCUjkCLMHZnp@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"
        
        self.conn = None
        
        # 35 Parameter definitions
        self.parameters = [
            'COG_01', 'COG_02', 'COG_03', 'COG_04', 'COG_05', 'COG_06', 'COG_07', 'COG_08', 'COG_09',
            'COG_31', 'COG_32', 'COG_33',
            'SOC_10', 'SOC_11', 'SOC_12', 'SOC_13', 'SOC_14', 'SOC_15', 'SOC_16', 'SOC_17',
            'PER_18', 'PER_19', 'PER_20', 'PER_21', 'PER_22', 'PER_23', 'PER_24',
            'ETH_25', 'ETH_26', 'ETH_27', 'ETH_28', 'ETH_29', 'ETH_30', 'ETH_34', 'ETH_35'
        ]
        
        # Department templates
        self.department_templates = [
            {"name": "Engineering", "positions": ["Software Engineer", "Senior Engineer", "Lead Engineer", "Engineering Manager", "CTO"]},
            {"name": "Product Management", "positions": ["Product Manager", "Senior PM", "Principal PM", "VP Product"]},
            {"name": "Sales", "positions": ["Sales Representative", "Account Executive", "Sales Manager", "VP Sales"]},
            {"name": "Marketing", "positions": ["Marketing Specialist", "Content Manager", "Marketing Manager", "CMO"]},
            {"name": "Human Resources", "positions": ["HR Specialist", "HR Business Partner", "HR Manager", "CHRO"]},
            {"name": "Finance", "positions": ["Financial Analyst", "Senior Analyst", "Finance Manager", "CFO"]},
            {"name": "Operations", "positions": ["Operations Coordinator", "Operations Manager", "VP Operations"]},
            {"name": "Customer Success", "positions": ["Customer Success Manager", "Senior CSM", "VP Customer Success"]},
            {"name": "Design", "positions": ["UX Designer", "Senior Designer", "Design Manager", "Design Director"]},
            {"name": "Data Science", "positions": ["Data Analyst", "Data Scientist", "Senior Data Scientist", "Head of Data"]}
        ]
        
        # Performance archetypes for realistic distributions
        self.performance_archetypes = [
            {"name": "High Performer", "weight": 0.15, "rating_boost": 0.8},
            {"name": "Solid Performer", "weight": 0.35, "rating_boost": 0.3},
            {"name": "Average Performer", "weight": 0.30, "rating_boost": 0.0},
            {"name": "Developing Performer", "weight": 0.15, "rating_boost": -0.4},
            {"name": "Struggling Performer", "weight": 0.05, "rating_boost": -0.8}
        ]

    async def connect_db(self):
        """Connect to the database"""
        try:
            # Parse the connection URL for Supabase compatibility
            if self.db_url.startswith('postgresql://'):
                # Add SSL mode for Supabase
                if '?' not in self.db_url:
                    self.db_url += '?sslmode=require'
                elif 'sslmode=' not in self.db_url:
                    self.db_url += '&sslmode=require'
            
            # Try direct connection first
            self.conn = await asyncpg.connect(
                self.db_url,
                server_settings={
                    'application_name': 'hr_synthetic_data_generator',
                    'jit': 'off'
                }
            )
            print("✅ Connected to database successfully")
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            print("🔧 Trying alternative connection method...")
            
            # Try parsing URL components for manual connection
            try:
                import urllib.parse as urlparse
                parsed = urlparse.urlparse(self.db_url)
                
                self.conn = await asyncpg.connect(
                    host=parsed.hostname,
                    port=parsed.port or 5432,
                    user=parsed.username,
                    password=parsed.password,
                    database=parsed.path.lstrip('/'),
                    ssl='require',
                    server_settings={
                        'application_name': 'hr_synthetic_data_generator'
                    }
                )
                print("✅ Connected to database successfully using alternative method")
            except Exception as e2:
                print(f"❌ Alternative connection method also failed: {e2}")
                print("\n🔍 TROUBLESHOOTING TIPS:")
                print("1. Verify your DATABASE_URL is correct")
                print("2. Check if your Supabase project is active")
                print("3. Ensure your database password is correct")
                print("4. Try using the direct connection (port 5432) instead of pooler (port 6543)")
                print("5. Make sure your IP is allowed in Supabase settings")
                raise e

    async def close_db(self):
        """Close database connection"""
        if self.conn:
            await self.conn.close()

    def generate_realistic_rating(self, base_rating: float, parameter_type: str, employee_archetype: dict) -> float:
        """Generate realistic rating based on employee archetype and parameter type"""
        
        # Base rating with archetype adjustment
        rating = base_rating + employee_archetype["rating_boost"]
        
        # Add parameter-specific variations
        parameter_modifiers = {
            'COG': 0.1,  # Cognitive parameters have slightly higher variance
            'SOC': 0.2,  # Social parameters vary more based on personality
            'PER': 0.15, # Performance parameters are somewhat predictable
            'ETH': 0.05  # Ethical parameters tend to be more stable
        }
        
        param_prefix = parameter_type[:3]
        modifier = parameter_modifiers.get(param_prefix, 0.1)
        
        # Add realistic noise
        noise = np.random.normal(0, modifier)
        rating += noise
        
        # Ensure rating stays within bounds
        rating = max(1.0, min(5.0, rating))
        
        return round(rating, 2)

    def generate_evidence_text(self, parameter_id: str, rating: float) -> str:
        """Generate realistic evidence text based on parameter and rating"""
        
        evidence_templates = {
            'COG_01': {
                'high': ["Consistently articulates how daily work connects to company mission", "Takes initiative to understand broader business impact", "Volunteers for projects aligned with personal values"],
                'medium': ["Shows adequate understanding of role purpose", "Occasionally discusses work meaning", "Generally aligned with company goals"],
                'low': ["Primarily focused on task completion", "Limited awareness of broader impact", "Views work as transactional"]
            },
            'COG_07': {
                'high': ["Regularly proposes innovative solutions", "Successfully implemented 3 creative process improvements", "Challenges conventional approaches effectively"],
                'medium': ["Occasionally suggests new ideas", "Shows creative thinking in team discussions", "Open to trying new approaches"],
                'low': ["Prefers established procedures", "Rarely contributes new ideas", "Resistant to change"]
            },
            'PER_24': {
                'high': ["Successfully led cross-functional initiative", "Team consistently exceeds goals under their guidance", "Mentors junior team members effectively"],
                'medium': ["Shows leadership potential in small projects", "Colleagues often seek their input", "Takes ownership of team deliverables"],
                'low': ["Struggles to motivate team members", "Difficulty making decisions under pressure", "Avoids leadership responsibilities"]
            },
            'SOC_17': {
                'high': ["Presentations are clear and engaging", "Written communication is concise and actionable", "Active listener who asks clarifying questions"],
                'medium': ["Generally communicates effectively", "Occasional need for clarification", "Responsive to feedback"],
                'low': ["Messages often require follow-up for clarity", "Struggles in group presentations", "Communication style can be confusing"]
            }
        }
        
        # Determine rating category
        if rating >= 4.0:
            category = 'high'
        elif rating >= 2.5:
            category = 'medium'
        else:
            category = 'low'
        
        # Get evidence template or use generic
        if parameter_id in evidence_templates:
            return random.choice(evidence_templates[parameter_id][category])
        else:
            generic_evidence = {
                'high': ["Consistently demonstrates strong performance in this area", "Exceeds expectations regularly", "Serves as role model for others"],
                'medium': ["Meets expectations in this area", "Shows steady improvement", "Occasionally demonstrates strong capability"],
                'low': ["Area identified for development", "Inconsistent performance", "Would benefit from additional support"]
            }
            return random.choice(generic_evidence[category])

    async def create_departments(self, count: int = 10) -> List[Department]:
        """Create realistic departments"""
        departments = []
        
        for i, dept_template in enumerate(self.department_templates[:count]):
            dept_id = str(uuid.uuid4())
            department = Department(
                id=dept_id,
                name=dept_template["name"]
            )
            departments.append(department)
            
            # Insert department into database
            await self.conn.execute("""
                INSERT INTO departments (id, name, description, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (id) DO NOTHING
            """, dept_id, dept_template["name"], f"{dept_template['name']} Department", datetime.now(), datetime.now())
        
        print(f"✅ Created {len(departments)} departments")
        return departments

    async def create_employees(self, departments: List[Department], count: int = 200) -> List[Employee]:
        """Create realistic employees with proper distributions"""
        employees = []
        
        # Determine employees per department
        employees_per_dept = count // len(departments)
        
        for dept in departments:
            dept_template = next(d for d in self.department_templates if d["name"] == dept.name)
            positions = dept_template["positions"]
            
            # Create employees for this department
            for i in range(employees_per_dept):
                emp_id = str(uuid.uuid4())
                
                # Select position based on seniority distribution
                position_weights = [0.4, 0.3, 0.2, 0.1] if len(positions) >= 4 else [1.0/len(positions)] * len(positions)
                position = np.random.choice(positions[:len(position_weights)], p=position_weights)
                
                # Generate realistic hire date (last 5 years)
                hire_date = fake.date_between(start_date='-5y', end_date='today')
                
                employee = Employee(
                    id=emp_id,
                    name=fake.name(),
                    email=fake.email(),
                    position=position,
                    department_id=dept.id,
                    hire_date=hire_date
                )
                employees.append(employee)
                
                # Insert employee into database
                await self.conn.execute("""
                    INSERT INTO employees (id, name, email, department_id, position, hire_date, status, is_active, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    ON CONFLICT (id) DO NOTHING
                """, emp_id, employee.name, employee.email, dept.id, position, hire_date, 'active', True, datetime.now(), datetime.now())
        
        # Assign managers (20% of employees are managers)
        managers = random.sample(employees, max(1, len(employees) // 5))
        for manager in managers:
            # Assign 3-8 direct reports
            potential_reports = [e for e in employees if e.department_id == manager.department_id and e.id != manager.id]
            direct_reports = random.sample(potential_reports, min(random.randint(3, 8), len(potential_reports)))
            
            for report in direct_reports:
                report.manager_id = manager.id
                await self.conn.execute("""
                    UPDATE employees SET manager_id = $1 WHERE id = $2
                """, manager.id, report.id)
        
        print(f"✅ Created {len(employees)} employees across {len(departments)} departments")
        return employees

    async def create_users(self, employees: List[Employee]):
        """Create user accounts for employees"""
        for employee in employees:
            user_id = str(uuid.uuid4())
            
            # Determine role based on position
            role = 'admin' if any(title in employee.position.lower() for title in ['ceo', 'cto', 'cfo', 'cmo', 'chro']) else 'employee'
            
            await self.conn.execute("""
                INSERT INTO users (id, email, employee_id, role, is_active, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (email) DO NOTHING
            """, user_id, employee.email, employee.id, role, True, datetime.now(), datetime.now())
        
        print(f"✅ Created user accounts for {len(employees)} employees")

    async def generate_parameter_ratings(self, employees: List[Employee]):
        """Generate comprehensive parameter ratings for all employees"""
        
        rating_count = 0
        
        for employee in employees:
            # Assign performance archetype to employee
            archetype = np.random.choice(
                self.performance_archetypes,
                p=[a["weight"] for a in self.performance_archetypes]
            )
            
            # Generate ratings across multiple time periods
            periods = [
                {"start": date.today() - timedelta(days=180), "end": date.today() - timedelta(days=90)},
                {"start": date.today() - timedelta(days=90), "end": date.today()},
            ]
            
            for period in periods:
                # Self-assessment (typically higher)
                await self._create_rating_set(employee, archetype, period, 'self', base_boost=0.3)
                
                # Manager assessment (most critical)
                if employee.manager_id:
                    await self._create_rating_set(employee, archetype, period, 'manager', base_boost=0.0)
                
                # Peer assessments (2-3 peers)
                peer_count = random.randint(2, 4)
                for _ in range(peer_count):
                    await self._create_rating_set(employee, archetype, period, 'peer', base_boost=-0.1)
                
                rating_count += len(self.parameters) * (2 + peer_count)  # self + manager + peers
        
        print(f"✅ Generated {rating_count} parameter ratings")

    async def _create_rating_set(self, employee: Employee, archetype: dict, period: dict, rater_type: str, base_boost: float = 0.0):
        """Create a complete set of parameter ratings for an employee"""
        
        for parameter_id in self.parameters:
            # Base rating around 3.0 with archetype and rater adjustments
            base_rating = 3.0 + archetype["rating_boost"] + base_boost
            
            # Generate realistic rating
            rating_value = self.generate_realistic_rating(base_rating, parameter_id, archetype)
            
            # Generate evidence
            evidence_text = self.generate_evidence_text(parameter_id, rating_value)
            
            # Confidence score (managers more confident, peers less so)
            confidence_scores = {'manager': 0.9, 'self': 0.8, 'peer': 0.7, 'system': 1.0}
            confidence = confidence_scores.get(rater_type, 0.8) + random.uniform(-0.1, 0.1)
            confidence = max(0.5, min(1.0, confidence))
            
            # Insert rating
            rating_id = str(uuid.uuid4())
            await self.conn.execute("""
                INSERT INTO employee_parameter_ratings 
                (id, employee_id, parameter_id, rating_value, rater_type, evidence_text, 
                 confidence_score, rating_period_start, rating_period_end, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                ON CONFLICT DO NOTHING
            """, rating_id, employee.id, parameter_id, rating_value, rater_type, evidence_text,
                confidence, period["start"], period["end"], datetime.now(), datetime.now())

    async def calculate_all_kpis(self, employees: List[Employee]):
        """Calculate KPIs for all employees"""
        kpi_codes = ['FRLP', 'IV', 'CHI']
        calculation_count = 0
        
        for employee in employees:
            for kpi_code in kpi_codes:
                try:
                    # Calculate KPI using the database function
                    result = await self.conn.fetchval(
                        "SELECT calculate_advanced_kpi($1, $2, $3, $4)",
                        employee.id, kpi_code, 
                        date.today() - timedelta(days=90), 
                        date.today()
                    )
                    calculation_count += 1
                except Exception as e:
                    print(f"Warning: Failed to calculate {kpi_code} for {employee.name}: {e}")
        
        print(f"✅ Calculated {calculation_count} KPI values")

    async def generate_ai_insights(self, employees: List[Employee]):
        """Generate sample AI insights for employees"""
        
        insight_types = ['risk_assessment', 'leadership_potential', 'development_recommendation']
        insights_created = 0
        
        # Generate insights for 30% of employees
        sample_employees = random.sample(employees, len(employees) // 3)
        
        for employee in sample_employees:
            insight_type = random.choice(insight_types)
            
            # Generate realistic AI insight data
            insight_data = self._generate_insight_data(employee, insight_type)
            
            insight_id = str(uuid.uuid4())
            await self.conn.execute("""
                INSERT INTO employee_ai_insights 
                (id, employee_id, insight_type, insight_data, confidence_score, model_version, is_actionable)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, insight_id, employee.id, insight_type, json.dumps(insight_data), 
                random.uniform(0.7, 0.95), "cerebras-llama-3.3-70B", True)
            
            insights_created += 1
        
        print(f"✅ Generated {insights_created} AI insights")

    def _generate_insight_data(self, employee: Employee, insight_type: str) -> dict:
        """Generate realistic AI insight data"""
        
        if insight_type == 'risk_assessment':
            return {
                "risk_level": random.choice(["low", "medium", "high"]),
                "risk_factors": random.sample([
                    "Workload management concerns",
                    "Team collaboration challenges", 
                    "Skill development gaps",
                    "Communication effectiveness",
                    "Goal alignment issues"
                ], random.randint(1, 3)),
                "recommendations": [
                    "Schedule regular one-on-one meetings",
                    "Provide targeted training opportunities",
                    "Consider workload redistribution"
                ],
                "confidence_score": random.uniform(0.7, 0.9)
            }
        
        elif insight_type == 'leadership_potential':
            return {
                "leadership_readiness": random.uniform(2.5, 4.5),
                "strengths": random.sample([
                    "Strategic thinking", "Team motivation", "Decision making",
                    "Communication skills", "Problem solving", "Emotional intelligence"
                ], random.randint(2, 4)),
                "development_areas": random.sample([
                    "Delegation skills", "Conflict resolution", "Public speaking",
                    "Change management", "Performance coaching"
                ], random.randint(1, 3)),
                "timeline": random.choice(["6-12 months", "1-2 years", "2-3 years"]),
                "confidence_score": random.uniform(0.75, 0.95)
            }
        
        else:  # development_recommendation
            return {
                "priority_areas": random.sample([
                    "Technical skills", "Leadership development", "Communication",
                    "Project management", "Strategic thinking", "Team collaboration"
                ], random.randint(2, 3)),
                "recommended_actions": [
                    "Enroll in leadership training program",
                    "Participate in cross-functional projects",
                    "Seek mentoring from senior leader",
                    "Attend industry conferences"
                ],
                "timeline": {
                    "3_months": "Complete skills assessment",
                    "6_months": "Begin development program",
                    "12_months": "Demonstrate improved capabilities"
                },
                "success_metrics": [
                    "360-degree feedback improvement",
                    "Project delivery success rate",
                    "Team satisfaction scores"
                ],
                "confidence_score": random.uniform(0.8, 0.95)
            }

    async def generate_performance_reviews(self, employees: List[Employee]):
        """Generate sample performance reviews"""
        
        # Create a review cycle
        cycle_id = str(uuid.uuid4())
        await self.conn.execute("""
            INSERT INTO performance_review_cycles 
            (id, name, description, type, start_date, end_date, status)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """, cycle_id, "Q4 2024 Performance Review", "Quarterly performance evaluation", 
            "quarterly", date.today() - timedelta(days=90), date.today(), "completed")
        
        reviews_created = 0
        for employee in employees:
            if employee.manager_id:  # Only create reviews for employees with managers
                review_id = str(uuid.uuid4())
                rating = random.randint(3, 5)
                
                await self.conn.execute("""
                    INSERT INTO performance_reviews 
                    (id, employee_id, reviewer_id, cycle_id, rating, comments, status, review_type)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """, review_id, employee.id, employee.manager_id, cycle_id, rating,
                    f"Performance review for {employee.name}. Shows {['developing', 'solid', 'strong', 'excellent'][rating-2]} performance.",
                    "completed", "quarterly")
                
                reviews_created += 1
        
        print(f"✅ Generated {reviews_created} performance reviews")

    async def print_statistics(self):
        """Print database statistics"""
        
        stats = {}
        
        # Parameter ratings
        stats['parameter_ratings'] = await self.conn.fetchval("SELECT COUNT(*) FROM employee_parameter_ratings")
        
        # Employees
        stats['employees'] = await self.conn.fetchval("SELECT COUNT(*) FROM employees")
        
        # Departments  
        stats['departments'] = await self.conn.fetchval("SELECT COUNT(*) FROM departments")
        
        # KPI calculations
        stats['kpi_calculations'] = await self.conn.fetchval("SELECT COUNT(*) FROM employee_advanced_kpi_values")
        
        # AI insights
        stats['ai_insights'] = await self.conn.fetchval("SELECT COUNT(*) FROM employee_ai_insights")
        
        # Performance reviews
        stats['performance_reviews'] = await self.conn.fetchval("SELECT COUNT(*) FROM performance_reviews")
        
        print("\n" + "="*50)
        print("📊 DATABASE STATISTICS")
        print("="*50)
        for key, value in stats.items():
            print(f"{key.replace('_', ' ').title()}: {value:,}")
        print("="*50)

    async def run_full_generation(self, employee_count: int = 200):
        """Run complete synthetic data generation"""
        
        print("🚀 Starting Comprehensive Synthetic Data Generation")
        print(f"Target: {employee_count} employees across 10 departments")
        print("="*60)
        
        try:
            await self.connect_db()
            
            # Step 1: Create departments
            departments = await self.create_departments(10)
            
            # Step 2: Create employees
            employees = await self.create_employees(departments, employee_count)
            
            # Step 3: Create user accounts
            await self.create_users(employees)
            
            # Step 4: Generate parameter ratings (this takes the longest)
            print("⏳ Generating parameter ratings (this may take a few minutes)...")
            await self.generate_parameter_ratings(employees)
            
            # Step 5: Calculate KPIs
            print("⏳ Calculating KPI values...")
            await self.calculate_all_kpis(employees)
            
            # Step 6: Generate AI insights
            await self.generate_ai_insights(employees)
            
            # Step 7: Generate performance reviews
            await self.generate_performance_reviews(employees)
            
            # Print final statistics
            await self.print_statistics()
            
            print("\n🎉 SYNTHETIC DATA GENERATION COMPLETED SUCCESSFULLY!")
            print("Your HR Dashboard is now populated with realistic data!")
            
        except Exception as e:
            print(f"❌ Error during data generation: {e}")
            raise
        finally:
            await self.close_db()

async def main():
    """Main execution function"""
    
    print("🎯 HR Dashboard - Synthetic Data Generator")
    print("35-Parameter Employee Evaluation System")
    print("="*60)
    
    # Get employee count from user or use default
    try:
        employee_count = int(input("Enter number of employees to generate (default: 200): ") or "200")
    except ValueError:
        employee_count = 200
    
    if employee_count < 10:
        print("❌ Minimum 10 employees required")
        return
    
    if employee_count > 1000:
        confirm = input(f"⚠️  {employee_count} employees will generate ~{employee_count * 35 * 4:,} parameter ratings. Continue? (y/N): ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            return
    
    generator = SyntheticDataGenerator()
    await generator.run_full_generation(employee_count)

if __name__ == "__main__":
    asyncio.run(main()) 