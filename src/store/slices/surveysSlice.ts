import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { supabase } from '../../lib/supabase';
import { Survey } from '../../types';

interface SurveysState {
  data: Survey[];
  loading: boolean;
  error: string | null;
}

const initialState: SurveysState = {
  data: [],
  loading: false,
  error: null,
};

// Fetch all surveys
export const fetchSurveys = createAsyncThunk<Survey[], void, { rejectValue: string }>(
  'surveys/fetchSurveys',
  async (_, { rejectWithValue }) => {
    try {
      const { data, error } = await supabase
        .from('surveys')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) throw error;
      return data || [];
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch surveys');
    }
  }
);

// Create new survey
export const createSurvey = createAsyncThunk<Survey, Omit<Survey, 'id' | 'created_at'>, { rejectValue: string }>(
  'surveys/createSurvey',
  async (surveyData, { rejectWithValue }) => {
    try {
      const { data, error } = await supabase
        .from('surveys')
        .insert([surveyData])
        .select('*')
        .single();

      if (error) throw error;
      return data;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to create survey');
    }
  }
);

// Update survey
export const updateSurvey = createAsyncThunk<Survey, Partial<Survey> & { id: string }, { rejectValue: string }>(
  'surveys/updateSurvey',
  async ({ id, ...surveyData }, { rejectWithValue }) => {
    try {
      const { data, error } = await supabase
        .from('surveys')
        .update(surveyData)
        .eq('id', id)
        .select('*')
        .single();

      if (error) throw error;
      return data;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to update survey');
    }
  }
);

// Delete survey
export const deleteSurvey = createAsyncThunk<string, string, { rejectValue: string }>(
  'surveys/deleteSurvey',
  async (id, { rejectWithValue }) => {
    try {
      const { error } = await supabase
        .from('surveys')
        .delete()
        .eq('id', id);

      if (error) throw error;
      return id;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to delete survey');
    }
  }
);

const surveysSlice = createSlice({
  name: 'surveys',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch surveys
      .addCase(fetchSurveys.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSurveys.fulfilled, (state, action: PayloadAction<Survey[]>) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchSurveys.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch surveys';
      })
      // Create survey
      .addCase(createSurvey.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createSurvey.fulfilled, (state, action: PayloadAction<Survey>) => {
        state.loading = false;
        state.data.unshift(action.payload);
      })
      .addCase(createSurvey.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to create survey';
      })
      // Update survey
      .addCase(updateSurvey.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateSurvey.fulfilled, (state, action: PayloadAction<Survey>) => {
        state.loading = false;
        const index = state.data.findIndex(survey => survey.id === action.payload.id);
        if (index !== -1) {
          state.data[index] = action.payload;
        }
      })
      .addCase(updateSurvey.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to update survey';
      })
      // Delete survey
      .addCase(deleteSurvey.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteSurvey.fulfilled, (state, action: PayloadAction<string>) => {
        state.loading = false;
        state.data = state.data.filter(survey => survey.id !== action.payload);
      })
      .addCase(deleteSurvey.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to delete survey';
      });
  },
});

export const { clearError } = surveysSlice.actions;
export default surveysSlice.reducer; 