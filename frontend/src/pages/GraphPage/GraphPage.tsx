import { ReactFlow, applyNodeChanges, applyEdgeChanges, addEdge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useEffect, useState,  useCallback, memo} from 'react';
import {useNavigate, useParams} from 'react-router-dom'

import { useAppDispatch, useAppSelector } from "../../redux/hooks"

const initialNodes = [
  { id: 'n1', position: { x: 0, y: 0 }, data: { label: 'Node 1' } },
  { id: 'n2', position: { x: 0, y: 100 }, data: { label: 'Node 2' } },
];

const initialEdges = [{ id: 'n1-n2', source: 'n1', target: 'n2' }];

export const GraphPage = () =>{
    const { id } = useParams()
    const navigate = useNavigate();

    const drugs = useAppSelector(state=>state.graph.drugs)

    const navigate_home = () => { 
        navigate('/computationBayes') 
        
    };

    useEffect(()=>{
        console.log(id)
    },[])

    const [nodes, setNodes] = useState(initialNodes);
    const [edges, setEdges] = useState(initialEdges);
    
    const onNodesChange = useCallback(
        (changes) => setNodes((nodesSnapshot) => applyNodeChanges(changes, nodesSnapshot)),
        [],
    );
    const onEdgesChange = useCallback(
        (changes) => setEdges((edgesSnapshot) => applyEdgeChanges(changes, edgesSnapshot)),
        [],
    );
    const onConnect = useCallback(
        (params) => setEdges((edgesSnapshot) => addEdge(params, edgesSnapshot)),
        [],
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