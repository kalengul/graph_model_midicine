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
    const [dimUnrelated, setDimUnrelated] = useState(false);
    const [showArrowheads, setShowArrowheads] = useState(false);

    const PREPARE = 'prepare'
    const EFFECT = 'side_e'

    const loadGraph = async () => {
        const response = await fetch('/api/v1/graph/visualization/');
        const data = await response.json();
        if (data.data) {
            setGraphData(data.data);
            setSelectedNodeId(null);
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

    useEffect(() => {
        if (graphData) {
            redrawGraph();
        }
    }, [graphData, selectedNodeId, hideSideEffects, hideGroup, dimUnrelated, showArrowheads]);

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
                setSelectedNodeId(null);
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

    const redrawGraph = () => {
        if (!graphData) return;

        let paths = null;
        let nodeId = selectedNodeId;

        if (nodeId) {
            const filtered = getFilterGraph(graphData, hideSideEffects, hideGroup);
            paths = findPaths(filtered, nodeId);
        }

        setFigure(buildFigure(
            graphData,
            hideSideEffects,
            hideGroup,
            paths,
            nodeId,
            dimUnrelated,
            showArrowheads
        ));
    };

    const handleCheckboxChange = () => {
        setHideSideEffects(prev => !prev);
    }

    const handleGroupCheckboxChange = () => {
        setHideGroup(prev => !prev);
    }

    const handleDimUnrelatedChange = () => {
        setDimUnrelated(prev => !prev);
    }

    const handleShowArrowheads = () => {
        setShowArrowheads(prev => !prev);
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
        setSelectedNodeId(node.id);
    };

    const buildFigure = (graph, hideSide=false, hideGroup=false, 
                         highlightPaths = null, highlightNodeId = null,
                         dimUnrelated = false, showArrowheads = false) => {
        if (!graph) return {};

        const { nodes, links } = getFilterGraph(graph, hideSide, hideGroup);

        const highlightNodeIds = new Set()
        const highlightLinkSet = new Set()

        if (highlightNodeId) {
            highlightNodeIds.add(highlightNodeId);
            if (highlightPaths) {
                highlightPaths.forEach(( { source, target } ) => {
                    highlightNodeIds.add(source);
                    highlightNodeIds.add(target);
                    highlightLinkSet.add(`${source}-${target}`);
                });
            }
        }

        const nodeX = [];
        const nodeY = [];
        const nodeText = [];
        const nodeColor = [];
        const nodeOpacity = [];

        const nodeSize = [];
        const nodeIdByIndex = [];
        const normalEdgeX = [];
        const normalEdgeY = [];
        const normalEdgeOpacity = [];

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

                const isTargetNode = (n.id === highlightNodeId);
                const isHighlighted = highlightNodeIds.has(n.id);

                nodeColor.push(isTargetNode ? "red" : getNodeColor(n.label));
                nodeSize.push(isTargetNode ? 40: 25);
                nodeIdByIndex.push(n.id);

                const opacity = dimUnrelated && highlightNodeId
                    ? (isHighlighted ? 1.0 : 0.2)
                    : 1.0;
                nodeOpacity.push(opacity);
            });
        });

        links.forEach(link => {
            const src = pos[link.source];
            const tgt = pos[link.target];
            if (!src || !tgt) return;

            const isHighlighted = highlightLinkSet.has(`${link.source}-${link.target}`);
            const xPair = [src.x, tgt.x, null];
            const yPair = [src.y, tgt.y, null];

            if (isHighlighted) {
                highlightEdgeX.push(...xPair);
                highlightEdgeY.push(...yPair);
            }
            else {
                normalEdgeX.push(...xPair);
                normalEdgeY.push(...yPair);
                const opacity = dimUnrelated && highlightNodeId ? 0.2 : 1.0;
                normalEdgeOpacity.push(opacity, opacity, opacity)
            }
        });

        const arrowAnnotations = [];
        if (showArrowheads && highlightPaths) {
            highlightPaths.forEach(({ source, target }) => {
                const srcPos = pos[source];
                const tgtPos = pos[target];
                if (!srcPos || !tgtPos) return;

                const dx = tgtPos.x - srcPos.x;
                const dy = tgtPos.y - srcPos.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                const shrink = 12

                let x1_adj = tgtPos.x;
                let y1_adj = tgtPos.y;

                if (dist > shrink) {
                    x1_adj = tgtPos.x - (dx / dist) * shrink;
                    y1_adj = tgtPos.y - (dy / dist) * shrink;
                }

                arrowAnnotations.push({
                    x: x1_adj,
                    y: y1_adj,
                    ax: srcPos.x,
                    ay: srcPos.y,
                    xref: 'x',
                    yref: 'y',
                    axref: 'x',
                    ayref: 'y',
                    showarrow: true,
                    arrowhead: 3,
                    arrowwidth: 1.5,
                    arrowsize: 1.5,
                    arrowcolor: '#504f4f'
                });
            });
        }

        return {
            data: [
                {
                    x: normalEdgeX,
                    y: normalEdgeY,
                    mode: 'lines',
                    line: { color: '#9a9d9dff', width: 1 },
                    hoverinfo: 'none',
                    opacity: normalEdgeOpacity.length > 0 ? normalEdgeOpacity : 1,
                },
                {
                    x: highlightEdgeX,
                    y: highlightEdgeY,
                    mode: 'lines',
                    line: { color: '#504f4fff', width: 3 },
                    hoverinfo: 'none'
                },
                { 
                    x: nodeX,
                    y: nodeY,
                    text: nodeText,
                    mode: 'markers',
                    marker: {
                        color: nodeColor,
                        size: nodeSize,
                        opacity: nodeOpacity,
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
                plot_bgcolor: 'white',
                annotations: arrowAnnotations
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
                <label htmlFor="graph-select">Выберите графы:</label>
                <div style={{
                    display: "flex",
                    gap: "10px",
                    alignItems: "flex-start",
                    marginTop: "5px"
                }}>
                    <select
                        id="graph-select"
                        multiple
                        value={selectedIds}
                        onChange={(e) => {
                            const options = Array.from(e.target.selectedOptions);
                            setSelectedIds(options.map((o) => o.value));
                        }}
                        style={{ minWidth: "250px", minHeight: "100px" }}
                    >
                        {graphList.map((g) => (
                            <option key={g.id} value={g.id}>
                                {g.name || `Graph #${g.id}`}
                            </option>
                        ))}
                    </select>
                    <div style={{ display: "flex",
                                    flexDirection: "column",
                                    gap: "8px",
                                    alignSelf: "flex-start",
                                    width: "max-content"
                                }}>
                        <button onClick={loadMergedGraph}
                                style={{ width: "100%",
                                         textAlign: "center",
                                         minWidth: "200px" }}>
                            Загрузить граф для выбранных ЛС
                        </button>
                        <button onClick={loadGraph}
                                style={{ width: "100%",
                                         textAlign: "center",
                                         minWidth: "200px",
                                         marginLeft: "0" }}>
                            Загрузить общий граф
                        </button>
                    </div>
                </div>
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
                <label className="filter-label">
                    <input type="checkbox"
                        checked={hideSideEffects}
                        onChange={handleCheckboxChange} />
                    Скрыть прямые побочные действия
                </label>
                <label className="filter-label">
                    <input type="checkbox"
                        checked={hideGroup}
                        onChange={handleGroupCheckboxChange} />
                    Скрыть группы ЛС
                </label>
                <label className="filter-label">
                    <input 
                        type="checkbox"
                        checked={dimUnrelated}
                        onChange={handleDimUnrelatedChange} />
                    Затемнять не связанные узлы
                </label>
                <label className="filter-label">
                    <input
                        type="checkbox"
                        checked={showArrowheads}
                        onChange={handleShowArrowheads} />
                    Показать направление
                </label>
            </div>
            {figure &&
                <div style={{
                    display: "flex",
                    justifyContent: "center",
                    width: "100%",
                    marginTop: "20px"
                }}>
                    <div style={{
                        width: "90%",
                        maxWidth: "1000px",
                        height: '600px'
                    }}>
                        <Plot 
                            data={figure.data} 
                            layout={figure.layout} 
                            config={figure.config} 
                            style={{ width: '100%', height: "100%" }}

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
                                }
                            }}
                        />
                    </div>
                </div>
            }
            {!figure && <p>Граф не загружен</p>}
        </div>
    );
}
