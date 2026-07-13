import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import interactionsReducer from './slices/interactionsSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    interactions: interactionsReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
