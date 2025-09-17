import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import axios from "axios";
import { IDrugElem } from "./DrugManageSlice";

export interface IGraphState{
    drugs: IDrugElem[]
    loadStatus: string;
    [key: string]: any;
}

const GraphSlice = createSlice({
    name: 'graph',
    initialState: {
        drugs: [],
        loadStatus: "",
    } as IGraphState,
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
})

export const {addValue,  initStates} = GraphSlice.actions; //Actions создаются автоматически, нужно просто достать через деструкторизацию
export default GraphSlice.reducer; //Формирование reduser из набора методов из redusers