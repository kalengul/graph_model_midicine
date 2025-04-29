import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit';
import axios from "axios";


// interface TrunkResult{
//   status: string | number
//   data: string
// }

export interface loginFormData {
  username:	string,
  password:	string,
}

export const login = createAsyncThunk('authSlice/login', async (data: loginFormData) => {
  try {
      const response = await axios.post('/api/accounts/login/',data, {
        headers:{'Content-Type': 'application/json'},
      });
      if(response.data.result.status===200) return {status: 200, data: response.data.data.token};
  } catch (error) {
      console.error(`Ошибка при авторизации:\n`, error);
      return { status: "err", data:`Ошибка при авторизации`}; // Возвращаем пустой массив при ошибке
  }
});

interface AuthState {
  user: null | { username: string; password: string };
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: false,
  loading: false,
  error: null,
};


const AuthSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
      loginStart(state) {
        state.loading = true;
        state.error = null;
      },
      loginSuccess(state, action: PayloadAction<{ user: any; token: string }>) {
        state.loading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.token = action.payload.token;
        localStorage.setItem('token', action.payload.token);
      },
      loginFailure(state, action: PayloadAction<string>) {
        state.loading = false;
        state.error = action.payload;
      },
      logout(state) {
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
        localStorage.removeItem('token');
      },
      clearError(state) {
        state.error = null;
      },
    },
  });
  
  export const { loginStart, loginSuccess, loginFailure, logout, clearError } = AuthSlice.actions;
  export default AuthSlice.reducer;
