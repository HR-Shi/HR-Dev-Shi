import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { supabase } from '../../lib/supabase';
import { DashboardOverview } from '../../types';

interface DashboardState {
  data: DashboardOverview | null;
  loading: boolean;
  error: string | null;
}

const initialState: DashboardState = {
  data: null,
  loading: false,
  error: null,
};

export const fetchDashboardData = createAsyncThunk<DashboardOverview, void, { rejectValue: string }>(
  'dashboard/fetchData',
  async (_, { rejectWithValue }) => {
    try {
      // Fetch all required data in parallel
      const [
        { data: employees, error: employeesError },
        { data: surveys, error: surveysError },
        { data: actionPlans, error: actionPlansError }
      ] = await Promise.all([
        supabase.from('employees').select('*'),
        supabase.from('surveys').select('*').eq('status', 'active'),
        // For now, we'll mock action plans since the table doesn't exist yet
        Promise.resolve({ data: [], error: null })
      ]);

      if (employeesError) throw employeesError;
      if (surveysError) throw surveysError;
      if (actionPlansError) throw actionPlansError;

      // Calculate metrics
      const totalEmployees = employees?.length || 0;
      const activeSurveys = surveys?.length || 0;
      const activeActionPlans = actionPlans?.length || 0;

      // Mock engagement calculations (in real app, this would come from survey responses)
      const avgEngagement = 75; // Mock value
      const highConcern = Math.floor(totalEmployees * 0.15);
      const midConcern = Math.floor(totalEmployees * 0.25);
      const goodStatus = totalEmployees - highConcern - midConcern;

      // Mock engagement trend (last 6 months)
      const engagementTrend = [70, 72, 74, 73, 75, 76];

      const dashboardData: DashboardOverview = {
        total_employees: totalEmployees,
        high_concern: highConcern,
        mid_concern: midConcern,
        good_status: goodStatus,
        avg_engagement: avgEngagement,
        active_surveys: activeSurveys,
        active_action_plans: activeActionPlans,
        engagement_trend: engagementTrend,
      };

      return dashboardData;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch dashboard data');
    }
  }
);

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchDashboardData.pending, (state: DashboardState) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDashboardData.fulfilled, (state: DashboardState, action: PayloadAction<DashboardOverview>) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchDashboardData.rejected, (state: DashboardState, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch dashboard data';
      });
  },
});

export default dashboardSlice.reducer; 