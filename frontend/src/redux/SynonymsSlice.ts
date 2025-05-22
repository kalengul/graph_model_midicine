import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit';
import axios from "axios";

interface ISynonymGroup{
    sg_id: string,
    sg_name: string,
    completed: boolean,
}

export interface ISynItemUpdate{
    s_id: string,
    is_changed: boolean,
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

interface ISynonymsState{
    SynonymGroupList: ISynonymGroup[],
    SynonymList: ISynonym[],
    SelectGr_id: string,
    message: string
}

const initialState: ISynonymsState = {
    SynonymGroupList: [],
    SynonymList: [],
    SelectGr_id: "",
    message: "",
}

const SynonymsSlice = createSlice({
    name: 'synonyms',
    initialState,
    reducers: {
        changeIsChange(state, action: PayloadAction<string>){
            const synonymIndex: number|undefined = state.SynonymList.findIndex(item=> item.s_id === action.payload)
            if(synonymIndex>=0) state.SynonymList[synonymIndex].is_changed = !state.SynonymList[synonymIndex].is_changed
        }
    },
    extraReducers: (builder) => {
        builder
        .addCase(fetchSynonymGroupList.fulfilled, (state, action: PayloadAction<IResultGet>) => {
            if(action.payload.status===200) state.SynonymGroupList=action.payload.data as ISynonymGroup[]
            else {
                state.message = action.payload.message
                state.SynonymGroupList = []
            }
        })
        .addCase(fetchSynonymList.fulfilled, (state, action: PayloadAction<IResultGet, string, { arg: string }>)=>{
            if(action.payload.status===200) {
                state.SynonymList = action.payload.data as ISynonym[]
                state.SelectGr_id = action.meta.arg
            }

            else {
                state.message = action.payload.message
                state.SynonymList = []
            }
        })
    }
})

export const {changeIsChange} = SynonymsSlice.actions;
export default SynonymsSlice.reducer;