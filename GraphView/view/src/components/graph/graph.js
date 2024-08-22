import React, { useState, useEffect, useRef} from 'react';
import * as d3 from 'd3';

import {Data} from "./graph_data.js"
import { DataParser } from './DataParser.js';

import './graph.css'

export const GraphView =() =>{
    const svgRef = useRef();

    const [graphData, setGraphData] = useState({'nodes': [], 'links':[]})

    useEffect(() => { //Перенести парсинг на сервер + получение данных идет с сервера
        const dataParser = new DataParser(Data)
        let newData = dataParser.Parse()

        setGraphData({'nodes': newData.nodes, 'links': newData.links})

    }, []);

    useEffect(() => {
        if (graphData && svgRef.current) {
            //console.log(svgRef.current)
            const svg = d3.select(svgRef.current);
            const width = 1000;
            const height = 500;

            // Очистка предыдущего графа
            svg.selectAll('*').remove();
            
            let links = svg.selectAll('.link')
            .data(graphData.links)
            .enter()
            .append('path')
            .attr('class', 'link')
            .attr('stroke', '#B8B5B5') // Цвет линии ребра
            .attr('stroke-width', 1) // Ширина линии ребра
            .style('pointer-events', 'none') //Отключение событий на ребрах (клики и т.д.)
            

            // Создание узлов
            let nodes = svg.selectAll('.node')
            .data(graphData.nodes) //Данные для узлов
            .enter()
            .append('circle')
            .attr('class', 'node')
            .attr('id', d => d.id)
            .attr('r', d => d.val) // Радиус узла
            .attr('fill', d=>d.color) // Цвет заполнения
            .attr("cursor", "pointer")
            .on('click', (event, d) => {
                // Добавьте логику для обработки клика по узлу
            })

            // Создание подписей узлов
            // nodes.append('text')
            // .text(d => d.name)
            // .attr('text-anchor', 'middle')
            // .attr('dominant-baseline', 'central');

           


            
            //Отрисовка элементов
            const simulation = d3.forceSimulation(graphData.nodes)
            .force('link', d3.forceLink(graphData.links).id(d => d.id))
            .force('charge', d3.forceManyBody().strength(-100)) // Отталкивание узлов
            .force('center', d3.forceCenter(width / 2, height / 2)) // Центрирование графа
            .force('x', d3.forceX(width / 2).strength(0.1))
            .force('y', d3.forceY(height / 2).strength(0.1)); // Центрирование графа

            simulation.on('tick', () => {
                links
                .attr("d", d => `M${d.source.x},${d.source.y} L${d.target.x},${d.target.y}`)

                nodes
                  .attr('cx', d => d.x)
                  .attr('cy', d => d.y);
            });
            
            //Наведение на узел:
            // Обработчик события mouseover для узлов
            nodes.on("mouseover", function(event, d) {
                // Находим все связанные ребра
                const linkedLinks = svg.selectAll(".link")
                     .filter(link => link.source.id === d || link.target.id === d)
                console.log(linkedLinks)
            
                // Находим все связанные узлы (кроме самого себя)
                const linkedNodes = svg.selectAll(".node")
                    .filter(node => node.id !== d && (
                            linkedLinks.filter(link => link.source.id === node.id || link.target.id === node.id).size() > 0
                    ));
                console.log(linkedNodes)
                
                // Несвязанные узлы
                const unlinkedNodes = svg.selectAll(".node")
                    .filter(node => (linkedLinks.filter(link => link.source.id === node.id || link.target.id === node.id).size() === 0))
                console.log(unlinkedNodes)
            
                // Выделяем ребра
                linkedLinks
                    .style("stroke", "black") 
                    .style("stroke-width", 1)
                    .style("opacity", 1);
            
                // Выделяем узлы
                linkedNodes
                    .style("fill", "steelblue");
                unlinkedNodes
                    .style("fill", "#D9D9D9")
            });
            
            // Обработчик события mouseout для узлов
            nodes.on("mouseout", function(event, d) {
                // Сбрасываем выделение ребер
                svg.selectAll(".link")
                    .style("stroke", '#B8B5B5') 
                    .style("stroke-width", 1)
                    .style("opacity", 1);
            
                // Сбрасываем выделение узлов
                svg.selectAll(".node")
                    .style("fill", d=>d.color); 
            });
        }
  
                

    }, [graphData]);
    
    return (
        <div className='Graphcontainer'>
            <svg ref={svgRef} className='svgGraph'> </svg>
        </div>
    )
}