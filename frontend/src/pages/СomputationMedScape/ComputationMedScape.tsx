import { ComputationMedScapeForm } from "../../components/computationMedScapeForm/computationMedScapeForm"
import { Nav } from "../../components/nav/nav"

import { useAppSelector } from "../../redux/hooks"


// import chevronRight from "../../../public/chevron-right.svg"

export const ComputationMedScape = () =>{
    const resultMedScape = useAppSelector(state=>state.computation.resultMedscape)
    return(
    <div className="flex">
        <Nav></Nav>
        <main className="ms-2 p-3 w-100">
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
            <h4>Результаты взаимодействия</h4>
            {
                resultMedScape && <div>
                    <p>{resultMedScape.compatibility_medscape}</p>
                    <p>{resultMedScape.description}</p>
                    <p>{resultMedScape.drugs}</p>
                </div>
            }

        </main>
    </div>
    )
}