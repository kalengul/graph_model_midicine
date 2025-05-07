import { Nav } from '../../components/nav/nav';

import { ComputationMedScapeForm } from "../../components/computationMedScapeForm/computationMedScapeForm"
import { ComputationResults } from "../../components/messageCards/computationResults/computationResults"

import { useAppSelector } from "../../redux/hooks"


// import chevronRight from "../../../public/chevron-right.svg"

export const ComputationMedScape = () =>{
    const resultMedScape = useAppSelector(state=>state.computation.resultMedscape)
    const isresultMedscape = useAppSelector(state => state.computation.isresultMedscape)
    return(
        <div className="flex">
        <Nav></Nav>
        <main className="ms-2 p-3 w-100">
            <h1>Взаимодействие по MedScape</h1>
            <ComputationMedScapeForm/>
            <hr/>
            <h4>Результаты оценки совместимости</h4>
            {
                isresultMedscape &&  
                Array.isArray(resultMedScape) && resultMedScape.map(res=>
                    <div>
                        <h6>Проверяемые лекарственные средства: { Array.isArray(res.drugs) && res.drugs.join(", ")}</h6>
                        <h6 className="mt-3">Результаты: </h6>

                        <ComputationResults compatibility={res.compatibility_medscape} />

                        <h6 className="mt-3">Примечание:</h6>
                        <p>{res.description}</p>
                        <hr/>
                    </div>
                )
            }
        </main>
        </div>
    )
}