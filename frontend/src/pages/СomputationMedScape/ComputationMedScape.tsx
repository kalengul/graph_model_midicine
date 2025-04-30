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
            {/* <div className="w-75 mt-4 drugManage">
                <a className='link-dark' data-bs-toggle="collapse" href="#collapseComputationMedScape" role="button" aria-expanded="false" aria-controls="collapseComputationMedScape">
                    <div className="flex ai-center">
                        <img className='me-2 chevron-icon' src={chevronRight} alt='chevronDown'/>
                        <h4>Ввести данные для расчета взаимодействия</h4>
                    </div>
                </a>
                <div className="collapse mt-4" id="collapseComputationMedScape">
                    <ComputationMedScapeForm/>
                </div>
            </div>
            <hr/> */}

            
            {/* <h4>Ввести данные для расчета взаимодействия</h4> */}
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