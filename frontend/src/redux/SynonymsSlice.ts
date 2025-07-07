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
    st_id: string | undefined,
}

export interface ISynStatus{
    st_id: string;
    st_name: string;
    st_code: string;
}

interface ISynonym{
    s_id: string,
    s_name: string,
    st_id: string | undefined,
}

interface IResultGet{
    status: number
    message: string
    data: ISynonymGroup[] | ISynonym[] | ISynStatus[]
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

        const data = {sg_id: state.synonyms.SelectGr?.sg_id, list_id: state.synonyms.updateList}
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

//Получение списка статусов синонимов
export const fetchSynStatusList = createAsyncThunk("synonyms/fetchSynStatusList", async ()=>{
    try {
        const response = await axios.get('/api/getSynonymStatusList/', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
            },
        });
        if (response.data.result.status === 200) return {status: 200, message:"", data: response.data.data}
        else return {status: response.data.result.status, message: response.data.result.message, data:[]}
    } catch (error) {
        console.error('Ошибка при загрузке списка статусов синонимов:\n', error);
        return {status: 500, message:"Ошибка при загрузке списка статусов синонимов", data:[]}
    }
})

//Сохранение изменений цвете статуса синонимов
export const updateSynStatusColor  = createAsyncThunk("synonyms/updateSynStatusColor", async (data: {newColor: string, st_id: string})=>{
    if(!data.newColor || data.newColor==="" || !data.st_id) {
        console.error(`Некореектно заполненные данные для обновления цвета статуса синонимов:\n`);
        return {status: 500, message:"Некореектно заполненные данные для обновления цвета статуса синонимов", data:[]}
    }
    try {
        const send_data = {st_id: data.st_id, st_code: data.newColor}
        console.log(send_data)

        const response = await axios.put('/api/updateSynonymStatus/', send_data, {
             headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            }
        })
        return {status: response.data.result.status, message: response.data.result.message, data:[]}
    } catch (error) {
        console.error(`Ошибка при обновлении цвета статуса синонимов:\n`, error);
        return {status: 500, message:"Ошибка при обновлении цвета статуса синонимов", data:[]}
    }
})

interface ISynonymsState{
    SynonymGroupList: ISynonymGroup[],
    SynonymList: ISynonym[],
    SelectGr: ISynonymGroup | undefined,
    updateList: ISynItemUpdate[], 
    synStatusList: ISynStatus[],
    activeStatus: ISynStatus | undefined,
    message: string
}

const initialState: ISynonymsState = {
    SynonymGroupList: [],
    SynonymList: [],
    synStatusList: [],
    SelectGr: undefined,
    activeStatus: undefined,
    updateList: [],
    message: "",
}

const SynonymsSlice = createSlice({
    name: 'synonyms',
    initialState,
    reducers: {
        changeColorStatus(state, action: PayloadAction<{st_id: string, newColor: string}>){
            const index = state.synStatusList.findIndex(st=>st.st_id == action.payload.st_id)
            if(index>=0) state.synStatusList[index].st_code = action.payload.newColor
        },
        chooseActiveStatus(state, action: PayloadAction<string>){
            if(state.activeStatus?.st_id == action.payload) state.activeStatus = undefined
            else state.activeStatus = state.synStatusList.find(st=>st.st_id == action.payload)
        },
        changeSynStatus(state, action: PayloadAction<string>){
            //Изменение состояния синонима для отображения
            // console.log(action.payload)
            const synonymIndex: number|undefined = state.SynonymList.findIndex(item=> item.s_id === action.payload)
            let newStatusId: string | undefined = undefined
            if(synonymIndex>=0) 
            {
                if(state.activeStatus?.st_id === state.SynonymList[synonymIndex].st_id) state.SynonymList[synonymIndex].st_id = undefined
                else {
                    state.SynonymList[synonymIndex].st_id = state.activeStatus?.st_id
                    newStatusId = state.activeStatus?.st_id
                }
            }
            
            //Добавление в список обновления
            if(state.updateList){
                const updateItem: ISynItemUpdate | undefined = state.updateList.find((elem: ISynItemUpdate) =>elem.s_id === action.payload)
                if(!updateItem) state.updateList.push({s_id: action.payload, st_id: newStatusId})
            }
            // if(state.updateList){
            //     const updateItem: ISynItemUpdate | undefined = state.updateList.find((elem: ISynItemUpdate) =>elem.s_id === action.payload.s_id)
            //     if(!updateItem) state.updateList.push(action.payload)
            //     else state.updateList = state.updateList.filter((elem: ISynItemUpdate) => elem.s_id !== action.payload.s_id)
            // }else{
            //     state.updateList = []
            //     state.updateList.push(action.payload)
            // }

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
                        state.SelectGr = undefined
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
                state.SelectGr = state.SynonymGroupList.find(sg=>sg.sg_id == action.meta.arg)
                state.updateList = []
            }

            else {
                state.SelectGr = undefined
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
        .addCase(fetchSynStatusList.fulfilled, (state, action: PayloadAction<IResultGet>)=>{
            if(action.payload.status===200) {
                state.synStatusList = action.payload.data as ISynStatus[]
            }

            else {
                state.message = action.payload.message
                state.synStatusList = []
            }
        })
        .addCase(updateSynStatusColor.fulfilled, (state, action: PayloadAction<IResultGet>)=>{
            state.message = action.payload.message
        })
    }
})

export const {changeColorStatus, changeSynStatus, chooseActiveStatus, initState} = SynonymsSlice.actions;
export default SynonymsSlice.reducer;