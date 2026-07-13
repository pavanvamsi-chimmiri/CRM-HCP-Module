import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { interactionsApi, InteractionFilters } from '@/services/api/interactions';
import { getErrorMessage } from '@/services/api/client';
import type { Interaction, InteractionStats } from '@/types';

interface InteractionsState {
  items: Interaction[];
  total: number;
  stats: InteractionStats | null;
  current: Interaction | null;
  isLoading: boolean;
  isSubmitting: boolean;
  isSummarizing: boolean;
  error: string | null;
}

const initialState: InteractionsState = {
  items: [],
  total: 0,
  stats: null,
  current: null,
  isLoading: false,
  isSubmitting: false,
  isSummarizing: false,
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

export const fetchInteraction = createAsyncThunk(
  'interactions/fetchOne',
  async (id: string, { rejectWithValue }) => {
    try {
      return await interactionsApi.get(id);
    } catch (error) {
      return rejectWithValue(getErrorMessage(error));
    }
  }
);

export const updateInteraction = createAsyncThunk(
  'interactions/update',
  async (
    { id, payload }: { id: string; payload: Parameters<typeof interactionsApi.update>[1] },
    { rejectWithValue }
  ) => {
    try {
      return await interactionsApi.update(id, payload);
    } catch (error) {
      return rejectWithValue(getErrorMessage(error));
    }
  }
);

export const summarizeVoiceNote = createAsyncThunk(
  'interactions/summarize',
  async (
    { text, doctorName }: { text: string; doctorName?: string },
    { rejectWithValue }
  ) => {
    try {
      return await interactionsApi.summarize(text, doctorName);
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
    clearCurrent: (state) => {
      state.current = null;
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
      .addCase(fetchInteraction.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchInteraction.fulfilled, (state, action) => {
        state.isLoading = false;
        state.current = action.payload;
      })
      .addCase(fetchInteraction.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      .addCase(updateInteraction.pending, (state) => {
        state.isSubmitting = true;
        state.error = null;
      })
      .addCase(updateInteraction.fulfilled, (state, action) => {
        state.isSubmitting = false;
        state.current = action.payload;
        const index = state.items.findIndex((i) => i.id === action.payload.id);
        if (index >= 0) {
          state.items[index] = action.payload;
        }
      })
      .addCase(updateInteraction.rejected, (state, action) => {
        state.isSubmitting = false;
        state.error = action.payload as string;
      })
      .addCase(summarizeVoiceNote.pending, (state) => {
        state.isSummarizing = true;
      })
      .addCase(summarizeVoiceNote.fulfilled, (state) => {
        state.isSummarizing = false;
      })
      .addCase(summarizeVoiceNote.rejected, (state, action) => {
        state.isSummarizing = false;
        state.error = action.payload as string;
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
        if (state.current?.id === action.payload) {
          state.current = null;
        }
      });
  },
});

export const { clearError, clearCurrent } = interactionsSlice.actions;
export default interactionsSlice.reducer;
