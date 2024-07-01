export class DataParser{
    constructor(data){
        this.inputData = data
    }

    Parse(){
        let outputData = {"nodes":[], "links": []}
        
        //Запись связей
        outputData.links.push(this.inputData.links)

        console.log(outputData)
    }
}