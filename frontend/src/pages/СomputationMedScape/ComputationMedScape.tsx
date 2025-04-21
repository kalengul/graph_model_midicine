import { ComputationMedScapeForm } from "../../components/computationMedScapeForm/computationMedScapeForm"
import { Nav } from "../../components/nav/nav"

export const ComputationMedScape = () =>{
    return(
    <div className="flex">
        <Nav></Nav>
        <main className="ms-2 p-3 w-100">
            <h1>Взаимодействие по MedScape</h1>
            <ComputationMedScapeForm/>
        </main>
    </div>
    )
}