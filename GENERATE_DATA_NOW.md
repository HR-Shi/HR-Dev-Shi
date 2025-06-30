# 🚀 **GENERATE SYNTHETIC DATA NOW!**
## Quick Start Guide

---

## **⚡ FASTEST METHOD (Windows)**

1. **Open PowerShell in the `backend` directory**
2. **Run this single command:**
   ```powershell
   .\run_synthetic_data.bat
   ```

That's it! The script will:
- ✅ Install all required packages automatically
- ✅ Generate 200 realistic employees
- ✅ Create 28,000+ parameter ratings
- ✅ Calculate all KPI values
- ✅ Generate AI insights

---

## **⚡ FASTEST METHOD (Mac/Linux)**

1. **Open Terminal in the `backend` directory**
2. **Run these commands:**
   ```bash
   chmod +x run_synthetic_data.sh
   ./run_synthetic_data.sh
   ```

---

## **🔧 MANUAL METHOD (All Platforms)**

1. **Install packages:**
   ```bash
   pip install -r requirements_synthetic.txt
   ```

2. **Run generator:**
   ```bash
   python generate_synthetic_data.py
   ```

3. **Choose employee count when prompted** (default: 200)

---

## **⚙️ DATABASE CONNECTION**

### **Option 1: Environment Variable (Recommended)**
Set your Supabase connection string:
```bash
# Windows PowerShell
$env:DATABASE_URL="postgresql://postgres:your_password@db.your_project_ref.supabase.co:5432/postgres"

# Mac/Linux Terminal
export DATABASE_URL="postgresql://postgres:your_password@db.your_project_ref.supabase.co:5432/postgres"
```

### **Option 2: Create .env File**
Create `.env` file in backend directory:
```
DATABASE_URL=postgresql://postgres:your_password@db.your_project_ref.supabase.co:5432/postgres
```

### **Option 3: Edit Script Directly**
Open `generate_synthetic_data.py` and update line 35:
```python
self.db_url = "postgresql://postgres:your_password@db.your_project_ref.supabase.co:5432/postgres"
```

---

## **📊 WHAT YOU'LL GET**

After running (with 200 employees):
- **10 Departments** with realistic hierarchies
- **200 Employees** with varied positions and backgrounds
- **28,000+ Parameter Ratings** across all 35 parameters
- **600 KPI Calculations** for FRLP, Innovation Velocity, and Collaborative Health
- **60 AI Insights** with risk assessments and development recommendations
- **Performance Reviews** with manager feedback
- **User Accounts** for authentication

---

## **⏱️ TIMING EXPECTATIONS**

| Employee Count | Approximate Time | Parameter Ratings Created |
|----------------|------------------|---------------------------|
| 50             | 2-3 minutes      | ~7,000                   |
| 200            | 5-8 minutes      | ~28,000                  |
| 500            | 15-20 minutes    | ~70,000                  |

---

## **🎯 VERIFICATION**

After completion, check your HR Dashboard:
1. **Go to Parameter Management page** - Should show all employees
2. **Check KPI Dashboard** - Should display charts and analytics
3. **Browse employee profiles** - Should show ratings and evidence
4. **Test AI Insights** - Should generate risk assessments

---

## **🎉 YOU'RE READY!**

Your HR Dashboard now has **enterprise-grade synthetic data** that showcases:
- ✅ 35-parameter evaluation system in action
- ✅ Advanced KPI calculations with real formulas
- ✅ AI-powered insights and recommendations
- ✅ Realistic performance distributions
- ✅ Professional visualizations and analytics

**Start exploring your data-rich HR Dashboard now!** 🚀 