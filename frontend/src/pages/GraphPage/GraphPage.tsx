import { ReactFlow, applyNodeChanges, applyEdgeChanges, addEdge, OnNodesChange, OnEdgesChange, OnConnect, Edge, Node
  ,} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useEffect, useState,  useCallback, useRef} from 'react';
import {/*useNavigate,*/ useParams} from 'react-router-dom'

import { LoadBar } from "../../components/loadBar/loadBar";

import { useAppDispatch, useAppSelector } from "../../redux/hooks"
import { fetchGraph, transformGraph} from '../../redux/GraphSlice';
// IGraphNode, IDraphLink, IGraph
// const initialNodes: Node[] = [
//   { id: '1', data: { label: 'Node 1' }, position: { x: 5, y: 5 } },
//   { id: '2', data: { label: 'Node 2' }, position: { x: 5, y: 100 } },
// ];
 
// const initialEdges: Edge[] = [{ id: 'e1-2', source: '1', target: '2' }];

export const GraphPage = () =>{
    const { id } = useParams()
    const dispatch = useAppDispatch()
    const containerRef = useRef<HTMLDivElement>(null);

    const drugs = useAppSelector(state=>state.graph.drugs)
    const loadStatus = useAppSelector(state=>state.graph.loadStatus)
    const graf = useAppSelector(state=>state.graph.showGraph)
    console.log(graf)

    useEffect(()=>{
        console.log(id)
        const idsArray = id?.split(",")
        if(idsArray) {
            //Получение графа по id
            dispatch(fetchGraph(idsArray))

            //Получение размеров окна для отображения
            if (containerRef.current) {
                const { width, height } = containerRef.current.getBoundingClientRect();
                console.log(width)
                console.log(height)

                //Преобразование графа для отображения
                dispatch(transformGraph({width: width, height: height}))
            }
            
        }
    },[])

    // const [nodes, setNodes] = useState(graf.nodes);
    // const [edges, setEdges] = useState(graf.links);

    const [nodes, setNodes] = useState<Node[]>([]);
    const [edges, setEdges] = useState<Edge[]>([]);
    
    // Обновляем локальное состояние когда меняются данные в Redux
    useEffect(() => {
        if (graf.nodes.length > 0) {
            setNodes(graf.nodes);
            setEdges(graf.links);
        }
    }, [graf.nodes, graf.links]);
    
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

//    // Функция для поиска всех связанных узлов (родителей и потомков)
//     const findConnectedNodes = useCallback((nodeId: string) => {
//         const node = nodes.find(n => n.id === nodeId);
//         if (!node) return [];
        
//         // Находим всех родителей (входящие связи)
//         const parents = getIncomers(node, nodes, edges);
        
//         // Находим всех потомков (исходящие связи)
//         const children = getOutgoers(node, nodes, edges);
        
//         // Объединяем и возвращаем уникальные ID
//         const allConnected = [...parents, ...children];
//         return Array.from(new Set(allConnected.map(n => n.id)));
//     }, [nodes, edges]);

//     // Обработчик наведения на узел
//     const onNodeMouseEnter = useCallback((event, node) => {
//         const connectedNodeIds = findConnectedNodes(node.id);
        
//         // Обновляем стили узлов
//         setNodes(nds => nds.map(n => {
//         const isConnected = connectedNodeIds.includes(n.id) || n.id === node.id;
        
//         return {
//             ...n,
//             style: {
//             ...n.style,
//             backgroundColor: isConnected ? '#ff6b6b' : '#fff',
//             border: isConnected ? '2px solid #ff5252' : '1px solid #ddd',
//             transition: 'all 0.3s ease'
//             }
//         };
//         }));

//         // Опционально: выделяем связанные связи
//         setEdges(eds => eds.map(edge => {
//         const isConnectedEdge = 
//             connectedNodeIds.includes(edge.source) || 
//             connectedNodeIds.includes(edge.target) ||
//             edge.source === node.id || 
//             edge.target === node.id;
        
//         return {
//             ...edge,
//             style: {
//             ...edge.style,
//             stroke: isConnectedEdge ? '#ff5252' : '#b1b1b7',
//             strokeWidth: isConnectedEdge ? 3 : 1,
//             },
//             animated: isConnectedEdge
//         };
//         }));
//     }, [findConnectedNodes, setNodes, setEdges]);

//     // Обработчик ухода курсора с узла
//     const onNodeMouseLeave = useCallback(() => {
//         // Восстанавливаем исходные стили
//         setNodes(nds => nds.map(n => ({
//         ...n,
//         style: {
//             ...n.style,
//             backgroundColor: '#fff',
//             border: '1px solid #ddd'
//         }
//         })));
        
//         setEdges(eds => eds.map(edge => ({
//         ...edge,
//         style: {
//             ...edge.style,
//             stroke: '#b1b1b7',
//             strokeWidth: 1,
//         },
//         animated: false
//         })));
//     }, [setNodes, setEdges]);




    return(
        <div className='ms-2 p-3'>
            {loadStatus === "loading" ? <LoadBar className="mt-4"/> 
            : (loadStatus === "reject" ? <div>Ошибка при получении графа</div>
            : 
            <>
                <h1>Граф</h1>
                <h5>Проверяемые лекарственные средства: {drugs.map(d=>d.drug_name).join(", ")}</h5>

                <div ref={containerRef} style={{ width: '97vw', height: '80vh', border: '1px solid #363845', borderRadius: "7px"}}>
                    <ReactFlow
                        nodes={nodes}
                        edges={edges}
                        onNodesChange={onNodesChange}
                        onEdgesChange={onEdgesChange}
                        onConnect={onConnect}
                        // onNodeMouseEnter={onNodeMouseEnter}
                        // onNodeMouseLeave={onNodeMouseLeave}
                        fitView
                    />
                </div>
            </>
            )}

        </div>
    )
}