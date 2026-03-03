import "./computationResults.scss"
import { IBannedPair, IBannedPairCont } from "../../../redux/Interfaces"

interface IComputationResultsProps{
    compatibility: string
    data?: IBannedPair[] | IBannedPairCont[] | null //Дополнительные данные для вывода в блоке
}

// const toUpperFirstSymbol = (str: string) =>{
//     if(str) return str.split("").map((s, index)=> index === 0 ? s.toLocaleUpperCase() : s).join("")
// }

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
                    <p><b>В введённом списке присутствует лекарственные средства, сочетание которых запрещено:</b></p>
                    {props.data && 
                        <div>
                            {props.data.map(e=>
                            <div>
                                {('pair' in e) && e.pair.join(" - ")}
                                {/* {e.pair[0]} - {e.pair[1]}  */}
                            </div>
                            )}
                        </div>
                    }
                </div>
            )
        case "banned-contraindications":
            return(
                <div className="ComputationResults incompatible">
                    <p><b>Примение запрещено в связи с индивидуальными противопоказаниями пациента</b></p>
                     {props.data && 
                        <div>
                            {props.data.map(e=>
                            <div>
                                <b>{('drug' in e) && `${e.drug}: `}</b>{('contraindications' in e) && e.contraindications.join("; ")} 
                            </div>
                            )}
                        </div>
                    }
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