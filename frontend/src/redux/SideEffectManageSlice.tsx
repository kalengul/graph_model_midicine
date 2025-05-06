import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import axios from "axios";

interface ISideEffectElem{
    id: string //ключ сохраняемого объекта
    se_name: string //значение для сохранения
}

interface IRankElem{
    se_id: string,
    drug_id: string,
    rank: string,
}

interface IStateSE {
    sideEffects: ISideEffectElem[]; // Указываем тип элементов массива
    ranks: IRankElem[];
    updateRanksList: IRankElem[];
    loadStatus: string;
    [key: string]: any; // Если state может содержать другие динамические поля
}

export interface ISendSideEffectData{
    se_name: string,
}

export interface ISendSideEffectDataError{
    se_name?: string,
}

// Асинхронный Thunk для загрузки списка побочных эффектов с сервера
export const fetchSideEffectList = createAsyncThunk('sideEffectManage/fetchSideEffectList', async () => {
    try {
        const response = await axios.get('/api/getSideEffect/');
        if (response.data.result.status === 200) {
            return response.data.data;
        }
        return []; // Если статус не 200
    } catch (error) {
        console.error('Ошибка при загрузке списка побопчных эффектов:\n', error);
        return []; // Возвращаем пустой массив при ошибке
    }
});

export const fetchSideEffectRankList = createAsyncThunk('sideEffectManage/fetchSideEffectRankList', async () => {
    try {
        const response = await axios.get('/api/getRanks/');
        if (response.data.result.status === 200) {
            return response.data.data;
        }
        return []; // Если статус не 200
    } catch (error) {
        console.error('Ошибка при загрузке списка рангов побопчных эффектов:\n', error);
        return []; // Возвращаем пустой массив при ошибке
    }
});

export const updateSideEffectRankList = createAsyncThunk('sideEffectManage/updateSideEffectRankList', async (updateData: IRankElem[]) => {
    try {
        console.log(updateData)
        const data = {update_rsgs: updateData}
        console.log(data)
        const response = await axios.put('/api/updateRanks/', data , {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            }
        });
        if(response.data.result.status===200) return response.data.data;
    } catch (error) {
        console.error(`Ошибка при обновлении рангов:\n`, error);
        return `Ошибка при обновлении рангов`; // Возвращаем пустой массив при ошибке
    }
});

export const addSideEffect = createAsyncThunk('sideEffectManage/addSideEffect', async (data: ISendSideEffectData)=>{
    try {
        const response = await axios.post("/api/addSideEffect/", data, {
            headers: { 
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            },
        })
        if(response.data.result.status===200) return response.data.data;
    } catch (error) {
        console.error(`Ошибка при добавлении побочного эффекта  ${data.se_name}:\n`, error);
        return `Ошибка при добавлении побочного эффекта ${data.se_name}`;
    }
})

export const deleteSideEffect = createAsyncThunk('sideEffectManage/deleteSideEffect', async (id: string)=>{
    try {
        const response = await axios.delete(`/api/deleteSideEffect/`,  {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
            },
            params: { se_id: id } 
        })
    if(response.data.result.status===200) return id
    } catch (error) {
        console.error(`Ошибка при удалении побочного эффекта:\n`, error)
        return `Ошибка при удалении побочного эффекта`;
    }
})

const SideEffectManageSlice = createSlice({
    name: 'sideEffectManage',
    initialState: {
        sideEffects: [],
        ranks: [],
        updateRanksList: [],
        loadStatus: "",
    } as IStateSE,
    reducers: {
        addValue(state, action){
            for(const key in state){
                if (key === action.payload.title) {
                    state[key] = action.payload.value 
                }
            }
        },

        updateRank(state, action){
            const drug_id = action.payload.drug_id
            const se_id = action.payload.se_id
            const newRank = action.payload.value

            //Определяем индекс ранга для инзменения
            const updateIndex = state.ranks.findIndex(r => r.drug_id === drug_id && r.se_id === se_id)

            if(updateIndex>=0){ 
                if(state.ranks[updateIndex].rank === newRank) return

                state.ranks[updateIndex].rank = newRank //Обнавляем существующее значение для отображения

                //Обновляем объект для отправления на сервер
                const checkIndex = state.updateRanksList.findIndex(r => r.drug_id === drug_id && r.se_id === se_id)
                if(checkIndex>=0)  state.updateRanksList[checkIndex].rank = newRank
                else state.updateRanksList.push({se_id: se_id, drug_id: drug_id, rank: newRank,})
            }

        },

        initStates(state){
            state.sideEffects = []
            state.loadStatus =  ""
            state.ranks = []
            state.updateRanksList = []
        }
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchSideEffectList.pending, (state) => {
                state.loadStatus = 'loading';
            })
            .addCase(fetchSideEffectList.fulfilled, (state, action) => {
                state.loadStatus = 'succeeded';
                state.sideEffects = action.payload;
            })
            .addCase(fetchSideEffectRankList.pending, (state) => {
                state.loadStatus = 'loading';
            })
            .addCase(fetchSideEffectRankList.fulfilled, (state, action) => {
                state.loadStatus = 'succeeded';
                state.ranks = action.payload;
            })
            .addCase(addSideEffect.fulfilled, (state, action) => {
                // console.log(action.payload)
                state.sideEffects.push(action.payload); // Добавляем новый todo в список
            })
            .addCase(deleteSideEffect.fulfilled, (state, action)=>{
                state.sideEffects = state.sideEffects.filter(se => se.id!=action.payload)
            });
    }
})

export const {addValue,  updateRank, initStates} = SideEffectManageSlice.actions; //Actions создаются автоматически, нужно просто достать через деструкторизацию
export default SideEffectManageSlice.reducer; //Формирование reduser из набора методов из redusers