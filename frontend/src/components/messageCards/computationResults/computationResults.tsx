import "./computationResults.scss"
import { IBannedPair, IBannedPairCont, IRepRecommendation } from "../../../redux/Interfaces"


interface IComputationResultsProps{
    compatibility: string
    data?: IBannedPair[] | IBannedPairCont[] | null //Дополнительные данные для вывода в блоке
    recommendations?: IRepRecommendation[] | undefined
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
                    <h5 >Лекарственные средства совместимы</h5>
                </div>
            )
        case "incompatible":
            return(
                <div className="ComputationResults incompatible">
                    <h5><b>Лекарственные средства не рекомендуются к совместному применению</b></h5>
                    {props.recommendations && props.recommendations.length >0 && 
                    <div className="mt-3">
                        <h6>Рекомендации по замене лекарственных средств</h6>
                        {props.recommendations.map((rec, index)=>
                        <div className="mt-2">
                            <div>
                                <span className='me-3'><b>{index+1}.</b></span> 
                                <span><b>Группа {rec.group_name}</b></span>
                            </div>
                            <div className="ms-5">
                                {rec.drugs && rec.drugs.map(dr =>
                                    <div className="mb-1">
                                        <p><b>Лекарственное средство:</b> {dr.drug_name}</p>
                                        <p><b>Предлагаемые замены:</b> {dr.replace_drugs.join("; ")}</p>
                                    </div>
                                )}
                            </div>
                        </div>)}
                    </div>
                    }
                    {props.recommendations && props.recommendations.length == 0 &&
                    <div className="mt-3">
                        <span className='me-3'><b>Не удалось подобрать лекарственные средства для снижения риска</b></span> 
                    </div>
                    }
                </div>
            )
        case "caution":
            return(
                <div className="ComputationResults caution">
                    <h5 >Лекарственные средства можно применять с осторожностью</h5>
                </div>
            )
         case "banned":
            return(
                <div className="ComputationResults incompatible">
                    <h5><b>В введённом списке присутствуют лекарственные средства, сочетание которых запрещено:</b></h5>
                    {props.data && 
                    
                        <div>
                            {props.data.map(e=>
                            <>
                                <div>
                                    {('pair' in e) && e.pair.join(" - ")}
                                    {/* {e.pair[0]} - {e.pair[1]}  */}
                                </div>
                                <div className="mt-3">
                                     {('comment' in e) && (e.comment!==null) && <span><b>Причина:  </b>{e.comment}</span>}
                                </div>

                            </>
                            )}
                        </div>
                    }
                  
                </div>
            )
        case "banned-contraindications":
            return(
                <div className="ComputationResults incompatible">
                    <h5><b>Примение запрещено в связи с индивидуальными противопоказаниями пациента</b></h5>
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