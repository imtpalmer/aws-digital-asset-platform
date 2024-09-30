import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

// Thunk for confirming registration
export const confirmRegistration = createAsyncThunk(
  'auth/confirmRegistration',
  async (formData, { rejectWithValue }) => {
    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API_BASE_URL}/confirm_registration`,
        formData,
        { headers: { "Content-Type": "application/json" } }
      );
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Confirmation failed');
    }
  }
);

// Thunk for user login
export const loginUser = createAsyncThunk(
  'auth/loginUser',
  async (formData, { rejectWithValue }) => {
    console.log("Login process started with formData:", formData);

    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API_BASE_URL}/login`,
        formData,
        { headers: { "Content-Type": "application/json" } }
      );
      
      console.log("API response received:", response.data);

      const { AccessToken, IdToken } = response.data;

      if (!AccessToken || !IdToken) {
        console.error("Authentication failed: Missing AccessToken or IdToken.");
        throw new Error("Authentication failed: AccessToken or IdToken is missing.");
      }

      // Store tokens in localStorage
      localStorage.setItem("AccessToken", AccessToken);
      localStorage.setItem("IdToken", IdToken);
      console.log("Tokens stored in localStorage");

      // Decode token to get user information
      const decodedToken = jwtDecode(IdToken);
      console.log("Decoded token:", decodedToken);

      const username = decodedToken.username || decodedToken.email;
      console.log("Login successful for user:", username);

      return { username, AccessToken, IdToken };
    } catch (error) {
      const errorMessage = error.response?.data || 'Login failed';
      console.error("Login failed with error:", errorMessage);
      return rejectWithValue(errorMessage);
    }
  }
);

// Thunk for user registration
export const registerUser = createAsyncThunk(
  'auth/registerUser',
  async (formData, { rejectWithValue }) => {
    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API_BASE_URL}/register`,
        formData,
        { headers: { "Content-Type": "application/json" } }
      );

      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Registration failed');
    }
  }
);

export const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    AccessToken: null,
    IdToken: null,
    error: null,
  },
  reducers: {
    setAuthUser: (state, action) => {
      state.user = action.payload.username;
      state.AccessToken = action.payload.AccessToken;
      state.IdToken = action.payload.IdToken;
    },
    logout: (state) => {
      state.user = null;
      state.AccessToken = null;
      state.IdToken = null;
      localStorage.removeItem("AccessToken");
      localStorage.removeItem("IdToken");
    },
  },
  extraReducers: (builder) => {
    builder
      // Confirm Registration
      .addCase(confirmRegistration.fulfilled, (state, action) => {
        state.user = action.payload;
        state.error = null;
      })
      .addCase(confirmRegistration.rejected, (state, action) => {
        state.error = action.payload;
      })
      // Login User
      .addCase(loginUser.fulfilled, (state, action) => {
        state.user = action.payload.username;
        state.AccessToken = action.payload.AccessToken;
        state.IdToken = action.payload.IdToken;
        state.error = null;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.error = action.payload;
      })
      // Register User
      .addCase(registerUser.fulfilled, (state, action) => {
        state.user = action.payload.username;
        state.error = null;
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.error = action.payload;
      });
  },
});

export const { setAuthUser, logout } = authSlice.actions;
export default authSlice.reducer;