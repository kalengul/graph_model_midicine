import * as d3 from 'd3';

export const d3Graph=(props)=>{
    const graphData = props.graphData
    const svgRef = props.svgRef
    if (graphData && svgRef.current) {
        const width = 800;
        const height = 400;

        const svg = d3.select(svgRef.current)
        svg.selectAll("*").remove() // Очистка предыдущего графа

        svg.attr("width",  width) //Устанавливает атрибут width
        .attr("height",  height)
        .append("g").attr('class', 'group') //добавляет новый элемент, тег которого передается в метод в качестве параметра
        .call(d3.zoom().on("zoom", function () { // Масштабирование с помощью колесика мыши
            svg.select('g.group').attr("transform", d3.event.transform)
        }))

        //Отрисовка элементов
        const simulation = d3.forceSimulation(graphData.nodes)
        .force('link', d3.forceLink(graphData.links).id(d => d.id))
        .force('charge', d3.forceManyBody().strength(-100)) // Отталкивание узлов
        .force('center', d3.forceCenter(width / 2, height / 2)) // Центрирование графа
        .force('x', d3.forceX(width / 2).strength(0.1))
        .force('y', d3.forceY(height / 2).strength(0.1)); // Центрирование графа

        const svgGroup = svg.select('g.group')
        //Добавление ссылок
        let links = svgGroup.append("g").attr('class', 'links')
        .selectAll('.link')
        .data(graphData.links) //Добавление данных
        .enter() //Нужен для ввода дополнительных значений (так как data привязывает только первое)
        .append('path')
        .attr('class', 'link')
        .attr('stroke', '#B8B5B5') // Цвет линии ребра
        .attr('stroke-width', 1) // Ширина линии ребра
        .style('pointer-events', 'none') //(устанавливает стиль) Отключение событий на ребрах (клики и т.д.)

        // Создание узлов
        let nodes = svgGroup.append("g").attr('class', 'nodes')
        .selectAll('.node')
        .data(graphData.nodes)
        .enter()
        .append('g')
        .attr('class', 'node');

        nodes.append('circle')
        .attr('class', 'node')
        .attr('id', d => d.id)
        .attr('r', d => d.val) // Радиус узла
        .attr('fill', d=>d.color) // Цвет заполнения
        .attr("cursor", "pointer")
        .on('click', (event, d) => {
            // Добавьте логику для обработки клика по узлу
        });

        nodes.append('text')
        .text(d => d.name)
        .attr('x', 0)
        .attr('y', 0)
        .attr('fill', 'black')
        .attr('font-size', '5px')
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'middle')
        .attr('class', 'label')
        .selectAll('tspan')

    
        

        const labelSizeThreshold = 20; // Порог радиуса для отображения текста (при меньшем радиусе текст будет скрыт)

        

       //Обновление симуляции
       simulation.on('tick', () => {
            links.attr("d", d => `M${d.source.x},${d.source.y} L${d.target.x},${d.target.y}`);
 
            nodes.attr('transform', d => `translate(${d.x}, ${d.y})`); // Правильная позиция для групп
        });
       
        
        
        // //Наведение на узел:
        // // Обработчик события mouseover для узлов
        // nodes.on("mouseover", function(event, d) {
        //     // Находим все связанные ребра
        //     const linkedLinks = svg.selectAll(".link")
        //          .filter(link => link.source.id === d || link.target.id === d)
        //     console.log(linkedLinks)
        
        //     // Находим все связанные узлы (кроме самого себя)
        //     const linkedNodes = svg.selectAll(".node")
        //         .filter(node => node.id !== d && (
        //                 linkedLinks.filter(link => link.source.id === node.id || link.target.id === node.id).size() > 0
        //         ));
        //     console.log(linkedNodes)
            
        //     // Несвязанные узлы
        //     const unlinkedNodes = svg.selectAll(".node")
        //         .filter(node => (linkedLinks.filter(link => link.source.id === node.id || link.target.id === node.id).size() === 0))
        //     console.log(unlinkedNodes)
        
        //     // Выделяем ребра
        //     linkedLinks
        //         .style("stroke", "black") 
        //         .style("stroke-width", 1)
        //         .style("opacity", 1);
        
        //     // Выделяем узлы
        //     linkedNodes
        //         .style("fill", "steelblue");
        //     unlinkedNodes
        //         .style("fill", "#D9D9D9")
        // });
        
        // // Обработчик события mouseout для узлов
        // nodes.on("mouseout", function(event, d) {
        //     // Сбрасываем выделение ребер
        //     svg.selectAll(".link")
        //         .style("stroke", '#B8B5B5') 
        //         .style("stroke-width", 1)
        //         .style("opacity", 1);
        
        //     // Сбрасываем выделение узлов
        //     svg.selectAll(".node")
        //         .style("fill", d=>d.color); 
        // });
    }
}