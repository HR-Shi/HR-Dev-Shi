# 🎯 **SYNTHETIC DATA GENERATOR GUIDE**
## 35-Parameter Employee Evaluation System

This guide will help you populate your HR Dashboard with **high-quality, realistic synthetic data** to showcase the full power of your 35-parameter evaluation system.

---

## 📋 **WHAT THE GENERATOR CREATES**

### **Organizational Structure**
- **10 Realistic Departments**: Engineering, Product, Sales, Marketing, HR, Finance, Operations, Customer Success, Design, Data Science
- **200+ Employees** (configurable): Distributed across departments with realistic job titles and hierarchies
- **Manager-Employee Relationships**: 20% of employees as managers with 3-8 direct reports each
- **User Accounts**: Complete authentication system for all employees

### **Performance Data**
- **35 Parameter Ratings**: Every employee rated on all 35 parameters by:
  - **Self-assessments** (typically higher ratings)
  - **Manager evaluations** (most critical)
  - **Peer reviews** (2-4 peers per employee)
- **Multiple Time Periods**: Historical data across 6-month periods
- **Realistic Evidence**: Behavioral anchors and specific examples for each rating

### **Advanced Analytics**
- **3 KPI Calculations**: FRLP, Innovation Velocity, and Collaborative Health automatically calculated
- **Performance Archetypes**: 
  - High Performers (15%) - ratings 4.0-5.0
  - Solid Performers (35%) - ratings 3.5-4.5
  - Average Performers (30%) - ratings 2.5-3.5
  - Developing Performers (15%) - ratings 2.0-3.0
  - Struggling Performers (5%) - ratings 1.0-2.5

### **AI-Powered Insights**
- **Risk Assessments**: Burnout indicators and performance concerns
- **Leadership Potential**: Readiness scores and development timelines
- **Development Recommendations**: Personalized growth plans with success metrics

### **Performance Reviews**
- **Quarterly Review Cycles**: Complete performance review data
- **Manager Feedback**: Realistic comments and ratings
- **Review Status Tracking**: Completed, in-progress, and scheduled reviews

---

## 🚀 **QUICK START (2 METHODS)**

### **Method 1: One-Click Execution (Windows)**
```bash
# In backend directory
run_synthetic_data.bat
```

### **Method 2: One-Click Execution (Mac/Linux)**
```bash
# In backend directory
chmod +x run_synthetic_data.sh
./run_synthetic_data.sh
```

### **Method 3: Manual Execution**
```bash
# Install dependencies
pip install -r requirements_synthetic.txt

# Run generator
python generate_synthetic_data.py
```

---

## ⚙️ **CONFIGURATION OPTIONS**

### **Employee Count**
- **Default**: 200 employees
- **Minimum**: 10 employees
- **Maximum**: 1000+ employees (with performance warning)
- **Calculation**: Each employee gets ~140 parameter ratings (35 params × 4 raters)

### **Data Volume Examples**
| Employees | Parameter Ratings | KPI Values | AI Insights |
|-----------|------------------|------------|-------------|
| 50        | ~7,000          | 150        | 15          |
| 200       | ~28,000         | 600        | 60          |
| 500       | ~70,000         | 1,500      | 150         |

---

## 🎲 **DATA QUALITY FEATURES**

### **Realistic Distributions**
- **Bell Curve Performance**: Most employees in average range
- **Department Variations**: Different performance patterns by department
- **Seniority Correlations**: Senior roles typically have higher ratings
- **Consistency Checks**: Related parameters show correlated ratings

### **Evidence-Based Ratings**
- **Behavioral Anchors**: Specific examples for each rating level
- **Parameter-Specific Examples**: Tailored evidence for cognitive, social, performance, and ethical parameters
- **Performance Storytelling**: Coherent narrative across all parameters

### **Temporal Patterns**
- **Growth Trends**: Some employees show improvement over time
- **Seasonal Variations**: Realistic fluctuations in performance
- **Review Cycles**: Data aligns with standard HR review periods

---

## 📊 **DATABASE IMPACT**

### **Tables Populated**
- `departments` - 10 departments with descriptions
- `employees` - All employee records with realistic data
- `users` - Authentication accounts for all employees
- `employee_parameter_ratings` - Comprehensive rating data
- `employee_advanced_kpi_values` - Calculated KPI scores
- `employee_ai_insights` - AI-powered analysis results
- `performance_reviews` - Historical review data
- `performance_review_cycles` - Review periods and cycles

### **Data Relationships**
- **Referential Integrity**: All foreign keys properly linked
- **Cascade Operations**: Proper cleanup when records are deleted
- **Performance Indexes**: Optimized for dashboard queries

---

## 🔧 **CUSTOMIZATION OPTIONS**

### **Department Templates**
Modify `department_templates` in the script to add your own departments:
```python
{"name": "Custom Department", "positions": ["Role 1", "Role 2", "Manager"]}
```

### **Performance Archetypes**
Adjust the performance distribution by modifying `performance_archetypes`:
```python
{"name": "Custom Archetype", "weight": 0.20, "rating_boost": 0.5}
```

### **Parameter Evidence**
Add your own evidence templates in `generate_evidence_text()` method.

---

## 🛠️ **TROUBLESHOOTING**

### **Common Issues**

**❌ Database Connection Failed**
- Check your `DATABASE_URL` environment variable
- Ensure Supabase database is accessible
- Verify database credentials

**❌ Missing Dependencies**
```bash
pip install faker numpy asyncpg python-dotenv
```

**❌ Permission Errors**
- Ensure your database user has INSERT permissions
- Check Supabase RLS policies if enabled

**❌ Slow Performance**
- Large datasets (500+ employees) may take 5-10 minutes
- Consider running in smaller batches
- Monitor database connection limits

### **Performance Tips**
- **Start Small**: Test with 50 employees first
- **Monitor Resources**: Watch database CPU and memory usage
- **Batch Processing**: Large datasets are processed in chunks
- **Connection Pooling**: Script uses single connection for efficiency

---

## 📈 **VERIFICATION CHECKLIST**

After running the generator, verify your data:

### **Dashboard Checks**
- [ ] Employee list shows all created employees
- [ ] Parameter ratings display for multiple employees
- [ ] KPI calculations show realistic values
- [ ] Charts and visualizations populate correctly
- [ ] AI insights appear for sample employees

### **Database Verification**
```sql
-- Check employee count
SELECT COUNT(*) FROM employees;

-- Verify parameter ratings
SELECT COUNT(*) FROM employee_parameter_ratings;

-- Confirm KPI calculations
SELECT COUNT(*) FROM employee_advanced_kpi_values;

-- Check AI insights
SELECT COUNT(*) FROM employee_ai_insights;
```

### **Quality Checks**
- [ ] Rating distributions look realistic (bell curve)
- [ ] Evidence text varies by parameter and rating
- [ ] Manager-employee relationships are logical
- [ ] Department distributions are balanced
- [ ] KPI scores correlate with parameter ratings

---

## 🎯 **SAMPLE DATA PREVIEW**

### **Employee Record**
```
Name: Sarah Johnson
Position: Senior Software Engineer
Department: Engineering
Manager: Mike Chen (Engineering Manager)
Hire Date: 2021-03-15
```

### **Parameter Rating Example**
```
Parameter: COG_07 (Creative Problem Solving)
Rating: 4.2/5.0
Evidence: "Regularly proposes innovative solutions and successfully implemented 3 creative process improvements"
Rater: Manager
Confidence: 0.89
```

### **KPI Calculation**
```
FRLP (Future-Ready Leadership Potential): 3.78/5.0
- Strategic Thinking (PER_19): 4.1 × 0.30 = 1.23
- Systems Thinking (COG_32): 3.8 × 0.25 = 0.95
- Change Leadership (PER_24): 3.6 × 0.20 = 0.72
- Critical Thinking (COG_03): 3.9 × 0.15 = 0.59
- Adaptability (PER_18): 3.7 × 0.10 = 0.37
```

---

## 🎉 **NEXT STEPS**

1. **Run the Generator**: Use one of the methods above
2. **Access Your Dashboard**: Navigate to the Parameter Management and KPI Dashboard pages
3. **Explore the Data**: Browse employees, ratings, and analytics
4. **Test Features**: Try filtering, sorting, and generating AI insights
5. **Customize Further**: Modify the script for your specific needs

---

## 📞 **SUPPORT**

If you encounter any issues:
1. Check the console output for specific error messages
2. Verify your database connection and permissions
3. Ensure all dependencies are installed correctly
4. Review the troubleshooting section above

Your HR Dashboard now has **enterprise-grade synthetic data** that rivals real-world HR platforms! 🚀 