import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { supabase } from '../../lib/supabase';
import { Employee, Department } from '../../types';

interface EmployeesState {
  data: Employee[];
  departments: Department[];
  loading: boolean;
  error: string | null;
}

const initialState: EmployeesState = {
  data: [],
  departments: [],
  loading: false,
  error: null,
};

// Fetch all employees with department info
export const fetchEmployees = createAsyncThunk<Employee[], void, { rejectValue: string }>(
  'employees/fetchEmployees',
  async (_, { rejectWithValue }) => {
    try {
      const { data, error } = await supabase
        .from('employees')
        .select(`
          *,
          departments (
            id,
            name
          )
        `)
        .order('created_at', { ascending: false });

      if (error) throw error;
      return data || [];
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch employees');
    }
  }
);

// Fetch departments for dropdowns
export const fetchDepartments = createAsyncThunk<Department[], void, { rejectValue: string }>(
  'employees/fetchDepartments',
  async (_, { rejectWithValue }) => {
    try {
      const { data, error } = await supabase
        .from('departments')
        .select('*')
        .order('name');

      if (error) throw error;
      return data || [];
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch departments');
    }
  }
);

// Add new employee
export const addEmployee = createAsyncThunk<Employee, Omit<Employee, 'id' | 'created_at' | 'updated_at'>, { rejectValue: string }>(
  'employees/addEmployee',
  async (employeeData, { rejectWithValue }) => {
    try {
      const { data, error } = await supabase
        .from('employees')
        .insert([employeeData])
        .select(`
          *,
          departments (
            id,
            name
          )
        `)
        .single();

      if (error) throw error;
      return data;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to add employee');
    }
  }
);

// Update employee
export const updateEmployee = createAsyncThunk<Employee, Partial<Employee> & { id: string }, { rejectValue: string }>(
  'employees/updateEmployee',
  async ({ id, ...employeeData }, { rejectWithValue }) => {
    try {
      const { data, error } = await supabase
        .from('employees')
        .update({ ...employeeData, updated_at: new Date().toISOString() })
        .eq('id', id)
        .select(`
          *,
          departments (
            id,
            name
          )
        `)
        .single();

      if (error) throw error;
      return data;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to update employee');
    }
  }
);

// Delete employee
export const deleteEmployee = createAsyncThunk<string, string, { rejectValue: string }>(
  'employees/deleteEmployee',
  async (id, { rejectWithValue }) => {
    try {
      const { error } = await supabase
        .from('employees')
        .delete()
        .eq('id', id);

      if (error) throw error;
      return id;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to delete employee');
    }
  }
);

const employeesSlice = createSlice({
  name: 'employees',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch employees
      .addCase(fetchEmployees.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchEmployees.fulfilled, (state, action: PayloadAction<Employee[]>) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchEmployees.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch employees';
      })
      // Fetch departments
      .addCase(fetchDepartments.fulfilled, (state, action: PayloadAction<Department[]>) => {
        state.departments = action.payload;
      })
      // Add employee
      .addCase(addEmployee.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(addEmployee.fulfilled, (state, action: PayloadAction<Employee>) => {
        state.loading = false;
        state.data.unshift(action.payload);
      })
      .addCase(addEmployee.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to add employee';
      })
      // Update employee
      .addCase(updateEmployee.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateEmployee.fulfilled, (state, action: PayloadAction<Employee>) => {
        state.loading = false;
        const index = state.data.findIndex(emp => emp.id === action.payload.id);
        if (index !== -1) {
          state.data[index] = action.payload;
        }
      })
      .addCase(updateEmployee.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to update employee';
      })
      // Delete employee
      .addCase(deleteEmployee.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteEmployee.fulfilled, (state, action: PayloadAction<string>) => {
        state.loading = false;
        state.data = state.data.filter(emp => emp.id !== action.payload);
      })
      .addCase(deleteEmployee.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to delete employee';
      });
  },
});

export const { clearError } = employeesSlice.actions;
export default employeesSlice.reducer; 