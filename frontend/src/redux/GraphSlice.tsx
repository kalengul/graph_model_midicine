import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { Node, Edge, MarkerType} from '@xyflow/react';

import { nanoid } from '@reduxjs/toolkit'
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

export interface ITransformGraphNode{ //Узел графа
    id: string;
    name: string;
    label: string;
    level: number;
    x: number;
    y: number;
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

export interface ITransformGraph{ //Граф
    nodes: ITransformGraphNode[],
    links: IDraphLink[],
    name: string[],
    maxLevel: number,
}

export interface IShowGraph{
    nodes: Node[]
    links: Edge[]
}

const InitStateGraph: IGraph | ITransformGraph = {
    nodes: [],
    links: [],
    name: [],
    maxLevel: 0,
}

const InitShowGraph: IShowGraph = {
    nodes: [],
    links: []
}

export interface IGraphState{
    drugs: IDrugElem[]
    loadStatus: string;
    graph: IGraph
    transformGraph: ITransformGraph;
    showGraph: IShowGraph;
    [key: string]: any;
}

//Получение графа с сервера
export const fetchGraph = createAsyncThunk('graph/fetchGraph', async (id: string[]) => {
    const response = await axios.get('/api/graph/',  {
        params: { id: `[${id.join(", ")}]` } 
    });
    if (response.data.result.status === 200) {
        return response.data.data;
    }
});

const GraphSlice = createSlice({
    name: 'graph',
    initialState: {
        drugs: [],
        graph: InitStateGraph,
        transformGraph: InitStateGraph,
        showGraph: InitShowGraph,
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
            state.graph = InitStateGraph as IGraph
            state.transformGraph = InitStateGraph as ITransformGraph
            state.showGraph = InitShowGraph
            state.loadStatus = ""
        },

        transformGraph(state, action: PayloadAction<{width: number; height: number}>){
            // Группируем узлы по уровням для лучшего расположения
            const graphCopy: IGraph = JSON.parse(JSON.stringify(state.graph))
            const levelGroups: {[key: number]: IGraphNode[]} = {};

            graphCopy.nodes.forEach(node => {
                if (!levelGroups[node.level]) {
                    levelGroups[node.level] = [];
                }
                // console.log(node)
                levelGroups[node.level].push(node);
            });
    
            const transformNodes: Node[] = graphCopy.nodes.map(node => {
                const levelNodes = levelGroups[node.level];
                const nodeIndex = levelNodes.findIndex(n => n.id === node.id);
                
                // Равномерное распределение по горизонтали
                const DEFAULT_NODE_WIDTH = 110
                const totalWidth = action.payload.width; // Общая ширина области
                const spacing = totalWidth / (levelNodes.length + 1) + DEFAULT_NODE_WIDTH;
                const x = (nodeIndex + 1) * spacing;
                
                // Вертикальное расположение по уровням
                const levelHeight = action.payload.height / (graphCopy.maxLevel/4);
                const y = node.level * levelHeight + 50; // +50 для отступа сверху

                return {
                    id: node.id,
                    data: { 
                        label: node.name 
                    },
                    position: { x, y },
                };
                
            });

            const transformLinks: Edge[] = graphCopy.links.map(link => {
                return {
                    id: nanoid(), 
                    source: link.source, 
                    target: link.target,
                    markerEnd: {
                        type: MarkerType.Arrow,
                        width: 20,
                        height: 20,
                        // color: '#FF0072',
                    },
                    style: {
                        strokeWidth: 1,
                        // stroke: '#FF0072',
                    },
                }
            })

            // Обновляем состояние transformGraph
            state.showGraph = {
                nodes: transformNodes,
                links: transformLinks
            }
        }
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchGraph.pending, (state) => {
                state.loadStatus = 'loading';
            })
            .addCase(fetchGraph.fulfilled, (state, action) => {
                state.loadStatus = 'succeeded';
                
                state.graph = JSON.parse(JSON.stringify(action.payload));
            })
            .addCase(fetchGraph.rejected, (state)=>{
                state.loadStatus = 'reject';
            })
    },
})

export const {addValue,  initStates, transformGraph} = GraphSlice.actions; //Actions создаются автоматически, нужно просто достать через деструкторизацию
export default GraphSlice.reducer; //Формирование reduser из набора методов из redusers