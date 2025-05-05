import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit';
import axios from "axios";


interface IAuthData {
  token: string;
  username: string;
  role: string;
}

interface ITrunkResult{
  status: number
  data: IAuthData | string
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
        localStorage.setItem('username', response.data.data.username);
        localStorage.setItem('role', response.data.data.role);
        return {status: 200, data: response.data.data};
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
      localStorage.removeItem('username');
      localStorage.removeItem('role');
      return { status: 200, data: 'Выход из системы успешен' };
    }
    return {status: response.data.result.status, data: response.data.result.message}
    
  } catch (error) {
    console.error(`Ошибка при выходе:\n`, error);
    return { status: 500, data: `Ошибка при выходе` };
  }
});

interface AuthState {
  token: string | null;
  user: {
    username: string | null;
    role: string | null;
  }
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  token: localStorage.getItem('token'),
  user: {
    username:  localStorage.getItem('username'),
    role: localStorage.getItem('role'),
  },
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
        if(action.payload.status === 200 && typeof action.payload.data !== 'string') {
          state.isAuthenticated = true
          state.token = action.payload.data.token
          state.user.username = action.payload.data.username
          state.user.role = action.payload.data.role
          state.error = null;
        } else if(typeof action.payload.data == 'string') {
          state.error = action.payload.data
          state.isAuthenticated = false
        }
      })
      .addCase(logout.fulfilled, (state) => {
        state.loading = false;
        state.isAuthenticated = false;
        state.user.role = null;
        state.user.username = null;
        state.token = null;
        state.error = null;
      })
    },  
  });
  
  export const {clearError, checkAuth} = AuthSlice.actions;
  export default AuthSlice.reducer;
