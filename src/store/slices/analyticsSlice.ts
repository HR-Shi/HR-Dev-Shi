import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { supabase } from '../../lib/supabase';

interface AnalyticsData {
  surveyResponseRate: number;
  averagePerformanceRating: number;
  employeeSatisfaction: number;
  activeGoals: number;
  departmentPerformance: Array<{
    name: string;
    value: number;
  }>;
  surveyDistribution: Array<{
    name: string;
    value: number;
  }>;
  performanceTrends: Array<{
    name: string;
    value: number;
  }>;
  employeeEngagement: Array<{
    name: string;
    value: number;
  }>;
}

interface AnalyticsState {
  data: AnalyticsData | null;
  loading: boolean;
  error: string | null;
}

const initialState: AnalyticsState = {
  data: null,
  loading: false,
  error: null,
};

export const fetchAnalyticsData = createAsyncThunk<AnalyticsData, void, { rejectValue: string }>(
  'analytics/fetchData',
  async (_, { rejectWithValue }) => {
    try {
      // Calculate survey response rate
      const { data: surveys, error: surveysError } = await supabase
        .from('surveys')
        .select('*');

      if (surveysError) throw surveysError;

      const totalSurveys = surveys.length;
      const completedSurveys = surveys.filter(s => s.status === 'completed').length;
      const surveyResponseRate = totalSurveys > 0 ? (completedSurveys / totalSurveys) * 100 : 0;

      // Calculate average performance rating
      const { data: reviews, error: reviewsError } = await supabase
        .from('performance_reviews')
        .select('rating, status');

      if (reviewsError) throw reviewsError;

      const averageRating = reviews.length > 0
        ? reviews.reduce((acc, curr) => acc + curr.rating, 0) / reviews.length
        : 0;

      // Get department performance data
      const { data: departments, error: departmentsError } = await supabase
        .from('departments')
        .select('name, employees(performance_reviews(rating))');

      if (departmentsError) throw departmentsError;

      const departmentPerformance = departments.map(dept => ({
        name: dept.name,
        value: dept.employees.length > 0
          ? dept.employees[0].performance_reviews.reduce((acc, curr) => acc + curr.rating, 0) / dept.employees[0].performance_reviews.length
          : 0
      }));

      // Get survey distribution
      const surveyTypes = [...new Set(surveys.map(s => s.type))];
      const surveyDistribution = surveyTypes.map(type => ({
        name: type,
        value: surveys.filter(s => s.type === type).length
      }));

      // Get performance trends (last 6 months)
      const sixMonthsAgo = new Date();
      sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);

      const { data: monthlyReviews, error: monthlyReviewsError } = await supabase
        .from('performance_reviews')
        .select('rating, created_at')
        .gte('created_at', sixMonthsAgo.toISOString());

      if (monthlyReviewsError) throw monthlyReviewsError;

      const performanceTrends = Array.from({ length: 6 }, (_, i) => {
        const month = new Date();
        month.setMonth(month.getMonth() - i);
        const monthReviews = monthlyReviews.filter(r => 
          new Date(r.created_at).getMonth() === month.getMonth()
        );
        return {
          name: month.toLocaleString('default', { month: 'short', year: 'numeric' }),
          value: monthReviews.length > 0
            ? monthReviews.reduce((acc, curr) => acc + curr.rating, 0) / monthReviews.length
            : 0
        };
      }).reverse();

      // Get employee engagement data (example metrics)
      const employeeEngagement = [
        { name: 'High Engagement', value: 65 },
        { name: 'Medium Engagement', value: 25 },
        { name: 'Low Engagement', value: 10 }
      ];

      return {
        surveyResponseRate: Math.round(surveyResponseRate * 10) / 10,
        averagePerformanceRating: Math.round(averageRating * 10) / 10,
        employeeSatisfaction: 85, // Example metric
        activeGoals: reviews.filter(r => r.status === 'in_progress').length,
        departmentPerformance,
        surveyDistribution,
        performanceTrends,
        employeeEngagement
      };
    } catch (error) {
      if (error instanceof Error) {
        return rejectWithValue(error.message);
      }
      return rejectWithValue('Failed to fetch analytics data');
    }
  }
);

const analyticsSlice = createSlice({
  name: 'analytics',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAnalyticsData.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAnalyticsData.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchAnalyticsData.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch analytics data';
      });
  },
});

export const { clearError } = analyticsSlice.actions;
export default analyticsSlice.reducer; 