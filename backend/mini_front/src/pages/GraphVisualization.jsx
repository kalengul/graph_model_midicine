import { useState, useEffect } from "react";
import Plot from 'react-plotly.js';


export default function GraphVisualization() {
    const [graphData, setGraphData] = useState(null);
    const [figure, setFigure] = useState(null);
    const [searchValue, setSearchValue] = useState("");
    const [hideSideEffects, setHideSideEffects] = useState(false);
    const [hideGroup, setHideGroup] = useState(false);
    const [selectedNodeId, setSelectedNodeId] = useState(null);
    const [graphList, setGraphList] = useState([]);
    const [selectedIds, setSelectedIds] = useState([]);

    const PREPARE = 'prepare'
    const EFFECT = 'side_e'

    const loadGraph = async () => {
        const response = await fetch('/api/v1/graph/visualization/');
        const data = await response.json();
        if (data.data) {
            setGraphData(data.data);
            setFigure(buildFigure(data.data, hideSideEffects));
        }
    };

    useEffect(() => {
        fetch("/api/v1/graph/get_list/")
        .then((res) => res.json())
        .then((data) => {
            if (data.data) {
                setGraphList(data.data);
            }
        })
        .catch((err) => console.error("Ошибка загрузки списка графов", err))
        loadGraph();
    }, []);

    const loadMergedGraph = async () => {
        if (selectedIds.length === 0) {
            alert("Выберите граф!");
            return;
        }
        try {
            const query = encodeURIComponent('[' + selectedIds.join(',') + ']');
            const response = await fetch(`/api/v1/graph/merge/?ids=${query}`);
            const data = await response.json();
            if (data.data) {
                setGraphData(data.data);
                setFigure(buildFigure(data.data, hideSideEffects, hideGroup));
            } 
        } catch (e) {
            console.error("Ошибка загрузки merged-графа", e);
        }
    }

    const getFilterGraph = (graph, hideSide, hideGroup) => {
        let nodes = [...graph.nodes];
        let links = [...graph.links];

        if (hideSide) {
            links = links.filter(link => {
                const srcNode = nodes.find(n => n.id === link.source);
                const tgtNode = nodes.find(n => n.id === link.target);
                return !((srcNode.label === PREPARE && tgtNode.label === EFFECT) ||
                         (srcNode.label === EFFECT && tgtNode.label === PREPARE));
            });
        }

        if (hideGroup) {
            const groupIds = new Set(nodes.filter(
                node => node.label === 'group').map(n => n.id));
            nodes = nodes.filter(n => !groupIds.has(n.id));

            links = links.filter(l => !groupIds.has(l.source) && !groupIds.has(l.target));
        }

        const connectedIds = new Set(links.flatMap(l =>[l.source, l.target]));
        nodes = nodes.filter(n => connectedIds.has(n.id));

        return {nodes, links};
    };

    const handleCheckboxChange = () => {
        setHideSideEffects(prev => {
            const newValue = !prev;
            if (graphData) {
               setFigure(buildFigure(graphData, newValue, hideGroup));
            }
            return newValue;
        });
    }

    const handleGroupCheckboxChange = () => {
        setHideGroup(prev => {
            const newValue = !prev;
            if (graphData) {
                setFigure(buildFigure(graphData, hideSideEffects, newValue));
            }
            return newValue;
        });
    }

    const handleSearch = () => {
        if (!graphData) return;
        const filtered = getFilterGraph(graphData, hideSideEffects, hideGroup);
        const nodeName = (searchValue || "").trim().toLowerCase();
        if (nodeName === "") {
            alert(`Введите название вершины`);
            return;
        }
        const node = filtered.nodes.find(n => String(n.name || '') .toLowerCase() === nodeName);
        if (!node) {
            alert(`Вершина "${searchValue}" не найдена`);
            return;
        }
        const paths = findPaths(filtered, node.id);
        setFigure(buildFigure(graphData, hideSideEffects, hideGroup,
            paths, node.id));
    };

    const buildFigure = (graph, hideSide=false, hideGroup=false, 
                         highlightPaths = null, highlightNodeId = null) => {
        if (!graph) return {};

        const { nodes, links } = getFilterGraph(graph, hideSide, hideGroup);

        const nodeX = [];
        const nodeY = [];
        const nodeText = [];
        const nodeColor = [];
        const edgeX = [];
        const edgeY = [];
        const nodeSize = [];
        const nodeIdByIndex = [];
        const normalEdgeX = [];
        const normalEdgeY = [];
        const highlightEdgeX = [];
        const highlightEdgeY = [];

        const levelNodes = [];
        nodes.forEach((n) => {
            const level = n.level || 0;
            if (!levelNodes[level]) levelNodes[level] = [];
            levelNodes[level].push(n);
        });

        const pos = {};
        Object.keys(levelNodes).forEach(level => {
            const arr = levelNodes[level];
            arr.forEach((n, i) => {
                const x = i * 200 - ((arr.length - 1) * 50);
                const y = -level * 200;
                pos[n.id] = { x, y };
                nodeX.push(x);
                nodeY.push(y);
                nodeText.push(`${n.name}\n(${n.label})`);
                nodeIdByIndex.push(n.id);

                if (highlightNodeId && n.id === highlightNodeId) {
                    nodeColor.push("red");
                    nodeSize.push(40);
                }
                else {
                    nodeColor.push(getNodeColor(n.label));
                    nodeSize.push(25);
                }
            });
        });

        links.forEach(link => {
            const src = pos[link.source];
            const tgt = pos[link.target];
            if (src && tgt) {
                const isHighlighted = highlightPaths &&
                    highlightPaths.some(p => p.source === link.source && p.target === link.target);
                if (isHighlighted) {
                    highlightEdgeX.push(src.x, tgt.x, null);
                    highlightEdgeY.push(src.y, tgt.y, null);
                }
                else {
                    normalEdgeX.push(src.x, tgt.x, null);
                    normalEdgeY.push(src.y, tgt.y, null);
                }
            }
        });

        return {
            data: [
                { x: normalEdgeX, y: normalEdgeY, mode: 'lines', line: { color: '#9a9d9dff', width: 1 }, hoverinfo: 'none' },
                { x: highlightEdgeX, y: highlightEdgeY, mode: 'lines', line: { color: '#504f4fff', width: 3 }, hoverinfo: 'none' },
                { 
                    x: nodeX,
                    y: nodeY,
                    text: nodeText,
                    mode: 'markers',
                    marker: {
                        color: nodeColor,
                        size: 20,
                        line: { color: 'darkblue', width:2 }
                    },
                    textposition: "top center",
                    hoverinfo: 'text',
                    textfont: { size: 12 }
                }
            ],
            layout: {
                width: 1000,
                height: 600,
                hovermode: 'closest',
                xaxis: { visible: false },
                yaxis: { visible: false },
                margin: {l: 50, r: 50, t: 50, b: 50 },
                showlegend: false,
                paper_bgcolor: 'white',
                plot_bgcolor: 'white'
            },
            config: { responsive: true, displayModeBar: true },
            nodeIdByIndex
        };
    };

    const getNodeColor = (label) => {
        const colors = {
            'prepare': '#54d68aff',
            'action': '#a674b9ff',
            'metabol': '#e9d069ff',
            'excretion': '#9050abff',
            'absorbtion': '#000000',
            'mechanism': '#499fd8ff',
            'group': '#884535',
            'noun': '#95A5A6',
            'side_e': '#e0685bff'
        };
        return colors[label] || 'lightgray';
    }

    const findPaths = (graph, startId) => {
        const links = graph.links || [];
        const visited = new Set();
        const pathEdges = [];

        const forwardQueue = [startId];
        while (forwardQueue.length > 0){
            const current = forwardQueue.shift();
            if (visited.has(`f-${current}`)) continue;
            visited.add(`f-${current}`);

            links.forEach(link => {
                if (link.source === current) {
                    pathEdges.push({ source: link.source, target: link.target });
                    forwardQueue.push(link.target);
                }
            });
        }

        const backwardQueue = [startId];
        while (backwardQueue.length > 0){
            const current = backwardQueue.shift();
            if (visited.has(`b-${current}`)) continue;
            visited.add(`b-${current}`);

            links.forEach(link => {
                if (link.target === current) {
                    pathEdges.push({ source: link.source, target: link.target });
                    backwardQueue.push(link.source);
                }
            });
        }

        return pathEdges;
    }

    return (
        <div className="form-page">
            <h2>Визуализация графа</h2>

            <div style={{ marginBottom: "15px" }}>
                <label>Выберите графы:</label>
                <select
                    multiple
                    value={selectedIds}
                    onChange={(e) => {
                        const options = Array.from(e.target.selectedOptions);
                        setSelectedIds(options.map((o) => o.value));
                    }}
                    style={{ marginLeft: "10px", minWidth: "250px", minHeight: "100px" }}
                >

                    {graphList.map((g) => (
                        <option key={g.id} value={g.id}>
                            {g.name || `Graph #${g.id}`}
                        </option>
                    ))}
                </select>
                <button onClick={loadMergedGraph} style={{ marginLeft: "10px" }}>
                    Загрузить граф для выбранных ЛС
                </button>
                <button onClick={loadGraph}>
                    Загрузить общий граф
                </button>
            </div>

            <div style={{ marginBottom: '10px' }}>
                <div className="search-bar">
                    <input
                    type="text"
                    placeholder="Поиск вершины"
                    value={searchValue}
                    onChange={e => setSearchValue(e.target.value)}
                    />
                    <button onClick={handleSearch}>Найти</button>
                </div>
                <label style={{  marginLeft: '10px'}}>
                    <input type="checkbox"
                        checked={hideSideEffects}
                        onChange={handleCheckboxChange} />
                    Скрыть прямые побочные действия
                </label>
                <label style={{  marginLeft: '10px'}}>
                    <input type="checkbox"
                        checked={hideGroup}
                        onChange={handleGroupCheckboxChange} />
                    Скрыть группы ЛС
                </label>
            </div>
            {figure &&
                <Plot 
                    data={figure.data} 
                    layout={figure.layout} 
                    config={figure.config} 
                    style={{ width: '100%', height: '600px' }}

                    onClick={(e) => {
                        if (!graphData || !figure.nodeIdByIndex) return;
                        if (e.points[0].curveNumber === 2) {
                            const pointIndex = e.points[0].pointIndex;
                            const nodeId = figure.nodeIdByIndex[pointIndex];

                            let newSelectedNodeId = nodeId;

                            if (selectedNodeId === nodeId) {
                                newSelectedNodeId = null;
                            }
                            setSelectedNodeId(newSelectedNodeId);

                            const filtered = getFilterGraph(
                                graphData, hideSideEffects, hideGroup);
                            const paths = newSelectedNodeId ? findPaths(filtered, newSelectedNodeId): null;
                            setFigure(buildFigure(graphData, hideSideEffects,
                                hideGroup, paths, newSelectedNodeId));
                        }
                    }}
                />
            }
            {!figure && <p>Граф не загружен</p>}
        </div>
    );
}
