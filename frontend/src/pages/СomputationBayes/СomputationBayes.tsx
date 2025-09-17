import { useEffect, useState } from "react"
// import {useNavigate} from 'react-router-dom'
import { Nav } from '../../components/nav/nav';
import { ComputationResults } from "../../components/messageCards/computationResults/computationResults"
import { CollapsList } from "../../components/collapsList/collapsList";
import { ComputationBayesForm } from '../../components/computationBayesForm/computationBayesForm';

import { useAppDispatch, useAppSelector } from "../../redux/hooks"
import { initResultBayes, initResultFortran, createCompareData} from "../../redux/ComputationSlice"
// import { fetchContraindicationssList } from "../../redux/ContraindicationsManageSlice";
import { addValue } from "../../redux/GraphSlice";

import {isRegex} from "../../assets/regex"

export const ComputationBayes = () =>{
    // const navigate = useNavigate();
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

    const data = useAppSelector(state=>state.computation.computationList)

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

    const ShowGraphHandker = () =>{
        const idsArray = data.map( e=> e.id).join(",")
        dispatch(addValue({title: "drugs", value: data}))
        // navigate(`/graph/${idsArray}`) 
        window.open(`/graph/${idsArray}`, '_blank');
    }

    return(
    <div className="flex">
        <Nav></Nav>
        <main className="ms-2 p-3 w-100">
            <h1>Взаимодействие по Байесу</h1>

            <ComputationBayesForm/>
            <hr/>
            
            {
                isresultBayes && isresultFortran && <div>
                    <h4>Результаты оценки совместимости</h4>
                    <h5>Проверяемые лекарственные средства: { Array.isArray(resultBayes.drugs) && resultBayes.drugs.join(" ")}</h5>
                    <h5 className="mt-3">Риски побочных эффектов: </h5>
                    <ComputationResults compatibility={resultBayes.сompatibility_bayes} />

                    {!isRegex(resultBayes.сompatibility_bayes, "banned")&&<div className="mt-3">
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
                        <div className="flex jc-sb mt-3">
                            <button className="btn send-btn" onClick={CompareWhithFortranHandler}>{compareTitle}</button>
                            <button className="btn send-btn" onClick={ ShowGraphHandker }>Отобразить граф</button>
                        </div>
                    </div>}
                </div>      
            }
        </main>
    </div>
    )
}