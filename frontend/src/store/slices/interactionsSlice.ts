import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { interactionsApi, InteractionFilters } from '@/services/api/interactions';
import { getErrorMessage } from '@/services/api/client';
import type { Interaction, InteractionStats } from '@/types';

interface InteractionsState {
  items: Interaction[];
  total: number;
  stats: InteractionStats | null;
  isLoading: boolean;
  isSubmitting: boolean;
  error: string | null;
}

const initialState: InteractionsState = {
  items: [],
  total: 0,
  stats: null,
  isLoading: false,
  isSubmitting: false,
  error: null,
};

export const fetchInteractions = createAsyncThunk(
  'interactions/fetchAll',
  async (filters: InteractionFilters | undefined, { rejectWithValue }) => {
    try {
      return await interactionsApi.list(filters);
    } catch (error) {
      return rejectWithValue(getErrorMessage(error));
    }
  }
);

export const fetchStats = createAsyncThunk(
  'interactions/fetchStats',
  async (_, { rejectWithValue }) => {
    try {
      return await interactionsApi.getStats();
    } catch (error) {
      return rejectWithValue(getErrorMessage(error));
    }
  }
);

export const createInteraction = createAsyncThunk(
  'interactions/create',
  async (payload: Parameters<typeof interactionsApi.create>[0], { rejectWithValue }) => {
    try {
      return await interactionsApi.create(payload);
    } catch (error) {
      return rejectWithValue(getErrorMessage(error));
    }
  }
);

export const deleteInteraction = createAsyncThunk(
  'interactions/delete',
  async (id: string, { rejectWithValue }) => {
    try {
      await interactionsApi.delete(id);
      return id;
    } catch (error) {
      return rejectWithValue(getErrorMessage(error));
    }
  }
);

const interactionsSlice = createSlice({
  name: 'interactions',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchInteractions.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchInteractions.fulfilled, (state, action) => {
        state.isLoading = false;
        state.items = action.payload.items;
        state.total = action.payload.total;
      })
      .addCase(fetchInteractions.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      .addCase(fetchStats.fulfilled, (state, action) => {
        state.stats = action.payload;
      })
      .addCase(createInteraction.pending, (state) => {
        state.isSubmitting = true;
        state.error = null;
      })
      .addCase(createInteraction.fulfilled, (state, action) => {
        state.isSubmitting = false;
        state.items.unshift(action.payload);
        state.total += 1;
      })
      .addCase(createInteraction.rejected, (state, action) => {
        state.isSubmitting = false;
        state.error = action.payload as string;
      })
      .addCase(deleteInteraction.fulfilled, (state, action) => {
        state.items = state.items.filter((i) => i.id !== action.payload);
        state.total -= 1;
      });
  },
});

export const { clearError } = interactionsSlice.actions;
export default interactionsSlice.reducer;
