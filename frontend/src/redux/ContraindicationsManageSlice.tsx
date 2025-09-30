//ContraindicationsManageSlice
import { createSlice, createAsyncThunk} from "@reduxjs/toolkit";
import axios from "axios";

export interface IContElem{
    cont_id: string;
    cont_name: string;
    cont_weigth: number;
}

// Асинхронный Thunk для загрузки списка противопоказаний с сервера
export const fetchContraindicationssList = createAsyncThunk('contraindicationsManage/fetchСontraindicationList', async () => {
    try {
        const response = await axios.get('/api/contraindications/');
        if (response.data.result.status === 200) {
            return response.data.data;
        }
        return []; // Если статус не 200
    } catch (error) {
        console.error('Ошибка при загрузке списка лекарственных средств:\n', error);
        return []; // Возвращаем пустой массив при ошибке
    }
});



interface IContraindicationsManageState {
    contraindications: IContElem[]; // Указываем тип элементов массива
    loadStatus: string;
    [key: string]: any; // Если state может содержать другие динамические поля
}

const ContraindicationsManageSlice = createSlice({
    name: 'contraindicationsManage',
    initialState: {
        contraindications: [],
        loadStatus: "",
    } as IContraindicationsManageState,
    reducers: {
        addValue(state, action){
            for(const key in state){
                if (key === action.payload.title) state[key] = action.payload.value
            }
        },

       initStates(state){
        state.contraindications = []
        state.loadStatus = ""
       }
    },
    extraReducers: (builder) => {
    builder
        .addCase(fetchContraindicationssList.pending, (state) => {
            state.loadStatus = 'loading';
        })
        .addCase(fetchContraindicationssList.fulfilled, (state, action) => {
            state.loadStatus = 'succeeded';
            state.contraindications = action.payload;
            // console.log(action.payload)
        })
    }
})

export const {addValue,  initStates} = ContraindicationsManageSlice.actions; //Actions создаются автоматически, нужно просто достать через деструкторизацию
export default ContraindicationsManageSlice.reducer; //Формирование reduser из набора методов из redusers