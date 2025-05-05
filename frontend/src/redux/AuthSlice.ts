import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit';
import axios from "axios";

interface ITrunkResult{
  status: number
  data: string
}

export interface ILoginFormData {
  username:	string,
  password:	string,
}

export interface ILoginFormDataError {
  username?:	string,
  password?:	string,
}

export const login = createAsyncThunk('authSlice/login', async (data: ILoginFormData) => {
  try {
      const response = await axios.post('/api/login/',data, {
        headers:{'Content-Type': 'application/json'},
      });
      if(response.data.result.status===200) {
        localStorage.setItem('token', response.data.data.token); //Сохраняем токен в localStorage
        return {status: 200, data: response.data.data.token};
      }
      return {status: response.data.result.status, data: response.data.result.message}
  } catch (error) {
      console.error(`Ошибка при авторизации:\n`, error);
      return { status: 500, data:`Ошибка при авторизации`}; // Возвращаем пустой массив при ошибке
  }
});

export const logout = createAsyncThunk('authSlice/logout', async () => {
  try {
    const response = await axios.post('/api/logout/', null, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      }
    );
    if(response.data.result.status == 200){
      localStorage.removeItem('token'); // Удаляем токен из localStorage при выходе
      return { status: 200, data: 'Выход из системы успешен' };
    }
    return {status: response.data.result.status, data: response.data.result.message}
    
  } catch (error) {
    console.error(`Ошибка при выходе:\n`, error);
    return { status: 500, data: `Ошибка при выходе` };
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
      clearError: (state) => { //Очистка ошибок
        state.error = null;
      },
      checkAuth: (state) => { //Проверка аутентификации при загрузки приложения
        const token = localStorage.getItem('token');
        if (token) {
          state.token = token;
          state.isAuthenticated = true;
        } else {
          state.token = null;
          state.isAuthenticated = false;
        }
      },
      
    },
    extraReducers: (builder) => {
      builder
      .addCase(login.fulfilled, (state, action: PayloadAction<ITrunkResult>) => {
        if(action.payload.status === 200) {
          state.isAuthenticated = true
          state.token = action.payload.data
          state.error = null;
        } else {
          state.error = action.payload.data
          state.isAuthenticated = false
        }
      })
      .addCase(logout.fulfilled, (state) => {
        state.loading = false;
        state.isAuthenticated = false;
        state.token = null;
        state.user = null;
        state.error = null;
      })
    },  
  });
  
  export const {clearError, checkAuth} = AuthSlice.actions;
  export default AuthSlice.reducer;
