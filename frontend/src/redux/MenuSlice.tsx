import { createSlice, createAsyncThunk} from "@reduxjs/toolkit";
import axios from "axios";

interface IMenuElem{
    title: string //ключ сохраняемого объекта
    slug: string //значение для сохранения
}

interface IMenuState {
    links: IMenuElem[]; // Указываем тип элементов массива
    isActive: string;
    loadStatus: string;
    [key: string]: any; // Если state может содержать другие динамические поля
}

// Асинхронный Thunk для загрузки menu с сервера
export const fetchMenu = createAsyncThunk('menu/fetchMenu', async () => {
    try {
        const response = await axios.get('/api/getMenu/');
        if (response.data.result.status === 200) {
            return response.data.data;
        }
        return []; // Если статус не 200
    } catch (error) {
        console.error('Ошибка при загрузке меню:\n', error);
        return []; // Возвращаем пустой массив при ошибке
    }
});

const MenuSlice = createSlice({
    name: 'menu',
    initialState: {
        links: [],
        isActive: "",
        loadStatus: "",
    } as IMenuState,
    reducers: {
        addValue(state, action){
            for(const key in state){
                if (key === action.payload.title) state[key] = action.payload.value
            }
        },

       initStates(state){
        state.isActive = ""
        state.links = []
         state.loadStatus = ""
       }
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchMenu.pending, (state) => {
                state.loadStatus = 'loading';
            })
            .addCase(fetchMenu.fulfilled, (state, action) => {
                state.loadStatus = 'succeeded';
                state.links = action.payload;
            })
    },


})

export const {addValue, initStates} = MenuSlice.actions; //Actions создаются автоматически, нужно просто достать через деструкторизацию
export default MenuSlice.reducer; //Формирование reduser из набора методов из redusers