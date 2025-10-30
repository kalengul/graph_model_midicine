import { ReactFlow, applyNodeChanges, applyEdgeChanges, addEdge, OnNodesChange, OnEdgesChange, OnConnect, Edge, Node} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useEffect, useState,  useCallback} from 'react';
import {/*useNavigate,*/ useParams} from 'react-router-dom'

import { useAppDispatch, useAppSelector } from "../../redux/hooks"
import { fetchGraph, IGraphNode, IDraphLink, IGraph} from '../../redux/GraphSlice';

const initialNodes: Node[] = [
  { id: '1', data: { label: 'Node 1' }, position: { x: 5, y: 5 } },
  { id: '2', data: { label: 'Node 2' }, position: { x: 5, y: 100 } },
];
 
const initialEdges: Edge[] = [{ id: 'e1-2', source: '1', target: '2' }];

export const GraphPage = () =>{
    const { id } = useParams()
    const dispatch = useAppDispatch()
    // const navigate = useNavigate();

    const drugs = useAppSelector(state=>state.graph.drugs)

    // const navigate_home = () => { 
    //     navigate('/computationBayes') 
        
    // };

    useEffect(()=>{
        console.log(id)
        const idsArray = id?.split(",")
        if(idsArray) {
            //Получение графа по id
            dispatch(fetchGraph(idsArray))


            //Преобразование графа для отображения
        }
    },[])

    const [nodes, setNodes] = useState(initialNodes);
    const [edges, setEdges] = useState(initialEdges);
    
    const onNodesChange: OnNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    [setNodes],
    ); 
    const onEdgesChange: OnEdgesChange = useCallback(
        (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
        [setEdges],
    );
    const onConnect: OnConnect = useCallback(
        (connection) => setEdges((eds) => addEdge(connection, eds)),
        [setEdges],
    );


    return(
        <div className='ms-2 p-3'>
            <h1>Граф</h1>
            <h5>Проверяемые лекарственные средства: {drugs.map(d=>d.drug_name).join(", ")}</h5>

            <div style={{ width: '95vw', height: '70vh' }}>
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onConnect={onConnect}
                    fitView
                />
            </div>

        </div>
    )
}