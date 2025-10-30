import { createSlice, createAsyncThunk} from "@reduxjs/toolkit";
import axios from "axios";
import { IDrugElem } from "./DrugManageSlice";

export interface IGraphNode{ //Узел графа
    id: string;
    name: string;
    label: string;
    level: number;
    parents: string[];
    weight: number;
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
export const fetchGraph = createAsyncThunk('graph/fetchGraph', async (id: string[]) => {
    try {
        const response = await axios.get('/api/graph/',  {
                params: { id: `[${id.join(", ")}]` } 
            });
        if (response.data.result.status === 200) {
            return response.data.data;
        }
        return []; // Если статус не 200
    } catch (error) {
        console.error('Ошибка при загрузке графа:\n', error);
        return []; // Возвращаем пустой массив при ошибке
    }
});

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