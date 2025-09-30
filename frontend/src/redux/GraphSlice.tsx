import { createSlice, /*createAsyncThunk*/ } from "@reduxjs/toolkit";
// import axios from "axios";
import { IDrugElem } from "./DrugManageSlice";

export interface IGraphNode{ //Узел графа
    id: string;
    name: string;
    label: string;
    level: number;
    parents: string[]
}

export interface IDraphLink{ //Связь графа
    source: string,
    target: string,
}

export interface IGraph{ //Граф
    nodes: IGraphNode[],
    links: IDraphLink[],
    name: string[],
    maxLevel: number,
}

const InitStateGraph: IGraph = {
    nodes: [],
    links: [],
    name: [],
    maxLevel: 0,
}

export interface IGraphState{
    drugs: IDrugElem[]
    loadStatus: string;
    graph: IGraph
    [key: string]: any;
}

//Получение графа с сервера

const GraphSlice = createSlice({
    name: 'graph',
    initialState: {
        drugs: [],
        graph: InitStateGraph,
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
        state.graph = InitStateGraph
        state.loadStatus = ""
       }
    },
})

export const {addValue,  initStates} = GraphSlice.actions; //Actions создаются автоматически, нужно просто достать через деструкторизацию
export default GraphSlice.reducer; //Формирование reduser из набора методов из redusers