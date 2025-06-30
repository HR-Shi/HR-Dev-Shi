import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import employeesReducer from './slices/employeesSlice';
import surveysReducer from './slices/surveysSlice';
import performanceReducer from './slices/performanceSlice';
import analyticsReducer from './slices/analyticsSlice';
import dashboardReducer from './slices/dashboardSlice';

export const store = configureStore({
    reducer: {
        auth: authReducer,
        employees: employeesReducer,
        surveys: surveysReducer,
        performance: performanceReducer,
        analytics: analyticsReducer,
        dashboard: dashboardReducer,
    },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch; 