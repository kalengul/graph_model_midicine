import "./computationResults.scss"

interface IComputationResultsProps{
    compatibility: string
}

export const ComputationResults = (props: IComputationResultsProps) =>{
    if(props.compatibility){
    switch (props.compatibility.trim()) {
        case "compatible":
            return(
                <div className="ComputationResults compatible">
                    <p >Лекарственные средства совместимы</p>
                </div>
            )
        case "incompatible":
            return(
                <div className="ComputationResults incompatible">
                    <p >Лекарственные средства несовместимы</p>
                </div>
            )
        case "caution":
            return(
                <div className="ComputationResults caution">
                    <p >Лекарственные средства можно применять с осторожностью</p>
                </div>
            )
         case "banned":
            return(
                <div className="ComputationResults incompatible">
                    <p >Лекарственные средства категорически запрещены для совместного применения</p>
                </div>
            )
        default:
            return(
                <div className="ComputationResults default">
                    <p >Статус совместимости лекарственных средств неизвестен</p>
                </div>
            )
    }
    }
}