import { useEffect, useState } from "react"
import { Nav } from '../../components/nav/nav';
import { CollapsList } from "../../components/collapsList/collapsList";
import { ComputationBayesForm } from '../../components/computationBayesForm/computationBayesForm';

import { useAppDispatch, useAppSelector } from "../../redux/hooks"
import { initResultBayes, initResultFortran, createCompareData} from "../../redux/ComputationSlice"

export const ComputationBayes = () =>{
    const [compareView, setCompareView] = useState(false)
    const [compareTitle, setCompareTitle] = useState("Показать сравнение с Фортраном")
    const dispatch = useAppDispatch()

    useEffect(()=>{
        dispatch(initResultBayes())
        dispatch(initResultFortran())
    }, [dispatch])
    const isresultBayes = useAppSelector(state=>state.computation.isresultBayes)
    const resultBayes = useAppSelector(state=>state.computation.resultBayes)

    const isresultFortran = useAppSelector(state=>state.computation.isresultFortran)
    const compareData = useAppSelector(state=>state.computation.compareSide_effects)

    useEffect(()=>{
        setCompareTitle("Показать сравнение с Фортраном")
        setCompareView(false)
    }, [isresultBayes, resultBayes])
   
    const CompareWhithFortranHandler = () =>{
        if (!compareView) {
            setCompareTitle("Скрыть сравнение с Фортраном")
            dispatch(createCompareData())
        }
        else setCompareTitle("Показать сравнение с Фортраном")
        setCompareView(!compareView)
    }

    return(
    <div className="flex">
        <Nav></Nav>
        <main className="ms-2 p-3 w-100">
            <h1>Взаимодействие по Байесу</h1>

            <ComputationBayesForm/>
            <hr/>
            <h4>Результаты оценки совместимости</h4>
            {
                isresultBayes && isresultFortran && <div>
                    <h5>Проверяемые лекарственные средства: { Array.isArray(resultBayes.drugs) && resultBayes.drugs.join(" ")}</h5>
                    <h5 className="mt-3">Риски побочных эффектов: </h5>

                    
                
                    {!compareView && resultBayes.side_effects &&
                        <CollapsList
                            title = ""
                            className="ComputationResults default"
                            type="riscs"
                            content= {resultBayes.side_effects[0].effects}
                        />
                    }
                    {
                        compareView && (compareData.length>0) && 
                        <CollapsList
                            title = ""
                            className="ComputationResults default"
                            type="compare-riscs"
                            content= {compareData}
                        />
                    }

                    <button className="btn send-btn mt-3" onClick={CompareWhithFortranHandler}>{compareTitle}</button>
                </div>      
            }
        </main>
    </div>
    )
}