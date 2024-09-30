import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import documentReducer from './slices/documentSlice';

const store = configureStore({
  reducer: {
    auth: authReducer,
    documents: documentReducer,
  },
});

export default store;