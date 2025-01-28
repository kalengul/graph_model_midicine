import * as d3 from 'd3';

export const d3RiskDiagram=(props)=>{

    const riskParams = props.riskParams
    const svgRef = props.svgRef
    const window = {width: props.size[0], height:  props.size[1], radius: props.radius}

    // Данные для трех секторов
    const data = [
        { label: "Разрешено", value: 1, color: "green" },
        { label: "С осторожностью", value: 1, color: "yellow" },
        { label: "Запрещено", value: 1, color: "red" }
    ];

    if (data&&svgRef.current){

        const pie = d3.pie();

        const svg = d3.select(svgRef.current)
        svg.selectAll("*").remove() // Очистка предыдущего графа

        svg.attr("width",  window.width) //Устанавливает атрибут width
        .attr("height",  window.height)
        .append("g").attr('class', 'group') //добавляет новый элемент, тег которого передается в метод в качестве параметра

        const svgGroup = svg.select('g.group')
        .data(pie(data))
    }
}
      