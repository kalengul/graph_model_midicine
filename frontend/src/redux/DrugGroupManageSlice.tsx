import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import axios from "axios";

interface IDrugGroupElem{
    id: string //ключ сохраняемого объекта
    dg_name: string //значение для сохранения
}

interface IDrugGroupManageState {
    drugGroups: IDrugGroupElem[]; // Указываем тип элементов массива
    loadStatus: string;
    [key: string]: any; // Если state может содержать другие динамические поля
}

// Асинхронный Thunk для загрузки списка групп ЛС с сервера
export const fetchDrugGroupList = createAsyncThunk('drugGroupManage/fetchDrugGroupList', async () => {
    try {
        const response = await axios.get('/api/getDrugGroup/');
        if (response.data.result.status === 200) {
            return response.data.data;
        }
        return []; // Если статус не 200
    } catch (error) {
        console.error('Ошибка при загрузке списка групп:\n', error);
        return []; // Возвращаем пустой массив при ошибке
    }
});

// Асинхронный Thunk для добавления новой группы ЛС
export const addDrugGroup = createAsyncThunk('drugGroupManage/addDrugGroup', async (dg_name: string) => {
    try {
        const data = new FormData();
        data.append('dg_name', dg_name)
        const response = await axios.post('/api/addDrugGroup/', data, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        if(response.data.result.status===200) return response.data.data;
    } catch (error) {
        console.error(`Ошибка при добавлении группы ${dg_name}:\n`, error);
        return `Ошибка при добавлении группы ${dg_name}`; // Возвращаем пустой массив при ошибке
    }
});



const DrugGroupManageSlice = createSlice({
    name: 'drugGroupManage',
    initialState: {
        drugGroups: [],
        loadStatus: ""
    } as IDrugGroupManageState,
    reducers: {
        addValue(state, action){
            for(const key in state){
                if (key === action.payload.title) {
                    state[key] = action.payload.value 
                }
            }
        },

       initStates(state){
        state.drugGroups = []
        state.loadStatus = ""
       }
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchDrugGroupList.pending, (state) => {
                state.loadStatus = 'loading';
            })
            .addCase(fetchDrugGroupList.fulfilled, (state, action) => {
                state.loadStatus = 'succeeded';
                state.drugGroups = action.payload;
            })
            .addCase(addDrugGroup.fulfilled, (state, action) => {
                state.drugGroups.push(action.payload); // Добавляем новый todo в список
            });
    },
})

export const {addValue,  initStates} = DrugGroupManageSlice.actions; //Actions создаются автоматически, нужно просто достать через деструкторизацию
export default DrugGroupManageSlice.reducer; //Формирование reduser из набора методов из redusers