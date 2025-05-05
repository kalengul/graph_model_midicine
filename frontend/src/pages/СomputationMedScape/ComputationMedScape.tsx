import { ComputationMedScapeForm } from "../../components/computationMedScapeForm/computationMedScapeForm"
import { ComputationResults } from "../../components/messageCards/computationResults/computationResults"

import { useAppSelector } from "../../redux/hooks"


// import chevronRight from "../../../public/chevron-right.svg"

export const ComputationMedScape = () =>{
    const resultMedScape = useAppSelector(state=>state.computation.resultMedscape)
    const isresultMedscape = useAppSelector(state => state.computation.isresultMedscape)
    return(
        <>
            <h1>Взаимодействие по MedScape</h1>
            <ComputationMedScapeForm/>
            <hr/>
            <h4>Результаты оценки совместимости</h4>
            {
                isresultMedscape && <div>
                    
                    <h5>Проверяемые лекарственные средства: { Array.isArray(resultMedScape.drugs) && resultMedScape.drugs.join(" ")}</h5>
                    <h5 className="mt-3">Результаты: </h5>

                    <ComputationResults compatibility={resultMedScape.compatibility_medscape} />

                    <h5 className="mt-3">Примечание:</h5>
                    <p>{resultMedScape.description}</p>
                </div>
            }
        </>
    )
}