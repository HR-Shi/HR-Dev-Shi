import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { supabase } from '../../lib/supabase';
import { PerformanceReview } from '../../types';

interface PerformanceState {
  data: PerformanceReview[];
  loading: boolean;
  error: string | null;
}

const initialState: PerformanceState = {
  data: [],
  loading: false,
  error: null,
};

// Fetch all performance reviews with employee data
export const fetchReviews = createAsyncThunk<PerformanceReview[], void, { rejectValue: string }>(
  'performance/fetchReviews',
  async (_, { rejectWithValue }) => {
    try {
      const { data, error } = await supabase
        .from('performance_reviews')
        .select(`
          *,
          employee:employees!employee_id (
            id,
            name,
            email,
            position
          ),
          reviewer:employees!reviewer_id (
            id,
            name,
            email,
            position
          )
        `)
        .order('created_at', { ascending: false });

      if (error) throw error;
      return data || [];
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch reviews');
    }
  }
);

// Create new performance review
export const createReview = createAsyncThunk<PerformanceReview, Omit<PerformanceReview, 'id' | 'created_at' | 'updated_at'>, { rejectValue: string }>(
  'performance/createReview',
  async (reviewData, { rejectWithValue }) => {
    try {
      const { data, error } = await supabase
        .from('performance_reviews')
        .insert([reviewData])
        .select(`
          *,
          employee:employees!employee_id (
            id,
            name,
            email,
            position
          ),
          reviewer:employees!reviewer_id (
            id,
            name,
            email,
            position
          )
        `)
        .single();

      if (error) throw error;
      return data;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to create review');
    }
  }
);

// Update performance review
export const updateReview = createAsyncThunk<PerformanceReview, Partial<PerformanceReview> & { id: string }, { rejectValue: string }>(
  'performance/updateReview',
  async ({ id, ...reviewData }, { rejectWithValue }) => {
    try {
      const { data, error } = await supabase
        .from('performance_reviews')
        .update({ ...reviewData, updated_at: new Date().toISOString() })
        .eq('id', id)
        .select(`
          *,
          employee:employees!employee_id (
            id,
            name,
            email,
            position
          ),
          reviewer:employees!reviewer_id (
            id,
            name,
            email,
            position
          )
        `)
        .single();

      if (error) throw error;
      return data;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to update review');
    }
  }
);

// Delete performance review
export const deleteReview = createAsyncThunk<string, string, { rejectValue: string }>(
  'performance/deleteReview',
  async (id, { rejectWithValue }) => {
    try {
      const { error } = await supabase
        .from('performance_reviews')
        .delete()
        .eq('id', id);

      if (error) throw error;
      return id;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to delete review');
    }
  }
);

const performanceSlice = createSlice({
  name: 'performance',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch reviews
      .addCase(fetchReviews.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchReviews.fulfilled, (state, action: PayloadAction<PerformanceReview[]>) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchReviews.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch reviews';
      })
      // Create review
      .addCase(createReview.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createReview.fulfilled, (state, action: PayloadAction<PerformanceReview>) => {
        state.loading = false;
        state.data.unshift(action.payload);
      })
      .addCase(createReview.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to create review';
      })
      // Update review
      .addCase(updateReview.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateReview.fulfilled, (state, action: PayloadAction<PerformanceReview>) => {
        state.loading = false;
        const index = state.data.findIndex(review => review.id === action.payload.id);
        if (index !== -1) {
          state.data[index] = action.payload;
        }
      })
      .addCase(updateReview.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to update review';
      })
      // Delete review
      .addCase(deleteReview.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteReview.fulfilled, (state, action: PayloadAction<string>) => {
        state.loading = false;
        state.data = state.data.filter(review => review.id !== action.payload);
      })
      .addCase(deleteReview.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to delete review';
      });
  },
});

export const { clearError } = performanceSlice.actions;
export default performanceSlice.reducer; 