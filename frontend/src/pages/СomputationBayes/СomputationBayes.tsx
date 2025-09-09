import { useEffect } from "react"
import { Nav } from '../../components/nav/nav';
import { CollapsList } from "../../components/collapsList/collapsList";
import { ComputationBayesForm } from '../../components/computationBayesForm/computationBayesForm';

import { useAppDispatch, useAppSelector } from "../../redux/hooks"
import { initResultBayes } from "../../redux/ComputationSlice"


export const ComputationBayes = () =>{
    const dispatch = useAppDispatch()
    useEffect(()=>{
        dispatch(initResultBayes())
    }, [dispatch])
    const isresultBayes = useAppSelector(state=>state.computation.isresultBayes)
    const resultBayes = useAppSelector(state=>state.computation.resultBayes)
    console.log(isresultBayes)
    console.log(resultBayes)

    return(
    <div className="flex">
        <Nav></Nav>
        <main className="ms-2 p-3 w-100">
            <h1>Взаимодействие по Байесу</h1>

            <ComputationBayesForm/>
            <hr/>
            <h4>Результаты оценки совместимости</h4>
            {
                isresultBayes && <div>
                    <h5>Проверяемые лекарственные средства: { Array.isArray(resultBayes.drugs) && resultBayes.drugs.join(" ")}</h5>
                    {/* <h5 className="mt-3">Результаты: </h5> */}
                    {/* <ComputationResults compatibility={resultFortran.сompatibility_fortran} /> */}

                    {/* {(resultFortran.сompatibility_fortran.trim()!=="banned") &&
                    <> */}
                        <h5 className="mt-3">Риски побочных эффектов: </h5>
                    
                        {resultBayes.side_effects &&
                            <CollapsList
                                title = "Высокий уровень риска появления побочных эффектов"
                                className="ComputationResults default"
                                type="riscs"
                                content= {resultBayes.side_effects[0].effects}
                            />
                        }

                    {/* </>} */}
                    </div>
            }
        </main>
    </div>
    )
}