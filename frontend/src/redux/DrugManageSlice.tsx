import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import axios from "axios";


interface IDrugElem {
    id: string,
    drug_name: string,
}

export interface ISendDrugData{
    drug_name: string,
}

export interface ISendDrugDataError{
    drug_name?: string,
}

interface IDrugsState {
    drugs: IDrugElem[]; // Указываем тип элементов массива
    loadStatus: string;
    [key: string]: any; // Если state может содержать другие динамические поля
}

// Асинхронный Thunk для загрузки списка ЛС с сервера
export const fetchDrugsList = createAsyncThunk('drugManage/fetchDrugsList', async () => {
    try {
        const response = await axios.get('/api/getDrug/');
        if (response.data.result.status === 200) {
            return response.data.data;
        }
        return []; // Если статус не 200
    } catch (error) {
        console.error('Ошибка при загрузке списка лекарственных средств:\n', error);
        return []; // Возвращаем пустой массив при ошибке
    }
});

// Асинхронный Thunk для добавления нового ЛС
export const addDrug = createAsyncThunk('drugManage/addDrug', async (formData: ISendDrugData) => {
    try {
        const data = new FormData();
        data.append('drug_name', formData.drug_name)
        const response = await axios.post('/api/addDrug/', data, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        if(response.data.result.status===200) return response.data.data;
    } catch (error) {
        console.error(`Ошибка при добавлении лекарственного средства  ${formData.drug_name}:\n`, error);
        return `Ошибка при добавлении лекарственного средства ${formData.drug_name}`; // Возвращаем пустой массив при ошибке
    }
});

export const deleteDrug = createAsyncThunk('drugManage/deleteDrug', async (id: string)=>{
    try {
        const response = await axios.delete(`/api/deleteDrug/`,  { params: { drug_id: id } })
        if(response.data.result.status===200) return id
    } catch (error) {
        console.error(`Ошибка при удалении лекарственного средства:\n`, error)
        return `Ошибка при удалении лекарственного средства`;
    }
})

const DrugManageSlice = createSlice({
    name: 'drugManage',
    initialState: {
        drugs: [],
        loadStatus: "",
    } as IDrugsState,
    reducers: {
        addValue(state, action){
            for(const key in state){
                if (key === action.payload.title) state[key] = action.payload.value
            }
        },

       initStates(state){
        state.drugs = []
        state.loadStatus = ""
       }
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchDrugsList.pending, (state) => {
                state.loadStatus = 'loading';
            })
            .addCase(fetchDrugsList.fulfilled, (state, action) => {
                state.loadStatus = 'succeeded';
                state.drugs = action.payload;
            })
            .addCase(addDrug.fulfilled, (state, action) => {
                state.drugs.push(action.payload); // Добавляем новый todo в список
            })
            .addCase(deleteDrug.fulfilled, (state, action)=>{
                state.drugs = state.drugs.filter(drug => drug.id != action.payload)
            });
    }
})

export const {addValue,  initStates} = DrugManageSlice.actions; //Actions создаются автоматически, нужно просто достать через деструкторизацию
export default DrugManageSlice.reducer; //Формирование reduser из набора методов из redusers