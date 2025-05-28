import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit';
import axios from "axios";
import { RootState } from './store';

interface ISynonymGroup{
    sg_id: string,
    sg_name: string,
    completed: boolean,
}

export interface ISynItemUpdate{
    s_id: string,
    status: boolean,
}

interface ISynonym{
    s_id: string,
    s_name: string,
    is_changed: boolean,
}

interface IResultGet{
    status: number
    message: string
    data: ISynonymGroup[] | ISynonym[]
}

//Получение списка групп синонимов
export const fetchSynonymGroupList = createAsyncThunk('synonyms/fetchSynonymGroupList', async ()=>{
    try {
        const response = await axios.get('/api/getSynonymGroups/', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
            },
        });
        if(response.data.result.status === 200) return {status: 200, message:"", data: response.data.data}
        else return {status: response.data.result.status, message: response.data.result.message, data:[]}
    } catch (error) {
        console.error('Ошибка при загрузке списка групп синонимов:\n', error);
        return {status: 500, message:"Ошибка при загрузке списка групп синонимов", data:[]}
    }
})

//Получение списка синонимов для группы
export const fetchSynonymList = createAsyncThunk("synonyms/fetchSynonymList", async (sg_id: string)=>{
    try {
        const response = await axios.get('/api/getSynonymList/', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
            },
            params: { sg_id: sg_id }
        });
        if (response.data.result.status === 200) return {status: 200, message:"", data: response.data.data}
        else return {status: response.data.result.status, message: response.data.result.message, data:[]}
    } catch (error) {
        console.error('Ошибка при загрузке списка синонимов:\n', error);
        return {status: 500, message:"Ошибка при загрузке списка синонимов", data:[]}
    }
})

//Сохранение обновлений синонимов на сервере
export const updateSynonymList = createAsyncThunk("synonyms/updateSynonymList", async(_, { getState })=>{
    try {
        // Получаем текущий state
        const state = getState()  as RootState;

        const data = {sg_id: state.synonyms.SelectGr_id, list_id: state.synonyms.updateList}
        console.log(data)

        const response = await axios.put('/api/updateSynonymList/', data, {
             headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            }
        })
        return {status: response.data.result.status, message: response.data.result.message, data:[]}
    } catch (error) {
        console.error(`Ошибка при обновлении синонимов:\n`, error);
        return {status: 500, message:"Ошибка при обновлении синонимов", data:[]}
    }
})

interface ISynonymsState{
    SynonymGroupList: ISynonymGroup[],
    SynonymList: ISynonym[],
    SelectGr_id: string,
    updateList: ISynItemUpdate[], 
    message: string
}

const initialState: ISynonymsState = {
    SynonymGroupList: [],
    SynonymList: [],
    SelectGr_id: "",
    updateList: [],
    message: "",
}

const SynonymsSlice = createSlice({
    name: 'synonyms',
    initialState,
    reducers: {
        changeIsChange(state, action: PayloadAction<ISynItemUpdate>){
            //Изменение состояния синонима для отображения
            const synonymIndex: number|undefined = state.SynonymList.findIndex(item=> item.s_id === action.payload.s_id)
            if(synonymIndex>=0) state.SynonymList[synonymIndex].is_changed = !state.SynonymList[synonymIndex].is_changed

            //Добавление в список обновления
            if(state.updateList){
                const updateItem: ISynItemUpdate | undefined = state.updateList.find((elem: ISynItemUpdate) =>elem.s_id === action.payload.s_id)
                if(!updateItem) state.updateList.push(action.payload)
                else state.updateList = state.updateList.filter((elem: ISynItemUpdate) => elem.s_id !== action.payload.s_id)
            }else{
                state.updateList = []
                state.updateList.push(action.payload)
            }

        },
        initState(state){
            state.updateList = []
        }
    },
    extraReducers: (builder) => {
        builder
        .addCase(fetchSynonymGroupList.fulfilled, (state, action: PayloadAction<IResultGet>) => {
            if(action.payload.status===200) 
                {
                    state.SynonymGroupList=action.payload.data as ISynonymGroup[]

                    if(action.payload.data.length === 0) {
                        state.SelectGr_id = ""
                        state.SynonymList = []
                        state.updateList = []
                    }
                }
            else {
                state.message = action.payload.message
                state.SynonymGroupList = []
                state.updateList = []
            }
        })
        .addCase(fetchSynonymList.fulfilled, (state, action: PayloadAction<IResultGet, string, { arg: string }>)=>{
            if(action.payload.status===200) {
                state.SynonymList = action.payload.data as ISynonym[]
                state.SelectGr_id = action.meta.arg
                state.updateList = []
            }

            else {
                state.message = action.payload.message
                state.SynonymList = []
                state.updateList = []
            }
        })
        .addCase(updateSynonymList.fulfilled, (state, action: PayloadAction<IResultGet>)=>{
            if(action.payload.status === 200){
                // console.log("Статус синонимов обновлен")
                state.updateList = []
            }
            else state.updateList = [] //Добавить откат исходного списка
        })
    }
})

export const {changeIsChange, initState} = SynonymsSlice.actions;
export default SynonymsSlice.reducer;