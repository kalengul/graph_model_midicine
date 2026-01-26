import { useEffect, useState } from "react"
// import {useNavigate} from 'react-router-dom'
import { Nav } from '../../components/nav/nav';
import { ComputationResults } from "../../components/messageCards/computationResults/computationResults"
import { CollapsList } from "../../components/collapsList/collapsList";
import { ComputationBayesForm } from '../../components/computationBayesForm/computationBayesForm';
import { LoadBar } from "../../components/loadBar/loadBar";

import { useAppDispatch, useAppSelector } from "../../redux/hooks"
import { initResultBayes, initResultFortran, addValue as addValueComputation} from "../../redux/ComputationSlice"
// import { fetchContraindicationssList } from "../../redux/ContraindicationsManageSlice";
import { addValue } from "../../redux/GraphSlice";

import {isRegex} from "../../assets/regex"
import { CreateCompareFunction, ICompareDataRisk } from "./CreateCompareData";
// import {SelectedType} from "./SelectedType"

export const ComputationBayes = () =>{
    // const navigate = useNavigate();
    const [compareView, setCompareView] = useState(false)
    const [compareTitle, setCompareTitle] = useState("Показать сравнение с Фортраном")
    const dispatch = useAppDispatch()

    useEffect(()=>{
        dispatch(initResultBayes())
        dispatch(initResultFortran())
        dispatch(addValueComputation({title: "compareStart", value: false}))
        
    }, [dispatch])
    const isresultBayes = useAppSelector(state=>state.computation.isresultBayes)
    const resultBayes = useAppSelector(state=>state.computation.resultBayes)

    // console.log(resultBayes)

    const isresultFortran = useAppSelector(state=>state.computation.isresultFortran)
    // const compareData = useAppSelector(state=>state.computation.compareSide_effects)
    const compareDtaFromDrug = useAppSelector(state=>state.computation.compareSide_effects_fromDrug)

    console.log(compareDtaFromDrug)

    const data = useAppSelector(state=>state.computation.computationList)

    useEffect(()=>{
        setCompareTitle("Показать сравнение с Фортраном")
        setCompareView(false)
    }, [isresultBayes, resultBayes])
   
    const resultFortran = useAppSelector(state=>state.computation.resultFortran)
    const [compareWithFortran, setCompareWithFortran] = useState<ICompareDataRisk[]>([])
    const CompareWhithFortranHandler = () =>{
        if (!compareView) {
            setCompareTitle("Скрыть сравнение с Фортраном")
            // dispatch(createCompareData())
            
            setCompareWithFortran(CreateCompareFunction(resultBayes.side_effects, resultFortran.side_effects))
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

    const isLoadFortran = useAppSelector(state=>state.computation.isLoadFortran)
    const isLoadBayes = useAppSelector(state=>state.computation.isLoadBayes)
    const compareStart = useAppSelector(state=>state.computation.compareStart)
    const fetchBayesStatus = useAppSelector(state=>state.computation.fetchBayesStatus)

    return(
    <div className="flex">
        <Nav></Nav>
        <main className="ms-2 p-3 w-100">
            <h1>Взаимодействие по Байесу</h1>

            <ComputationBayesForm/>
            <hr/>
            { compareStart &&
            (
                ((!isLoadFortran || !isLoadBayes) && (fetchBayesStatus === null))?(<LoadBar className="mt-4"/>)
                : ((!isLoadFortran || !isLoadBayes) && !fetchBayesStatus ? (<p>Для лекарственного средства нет графа</p>)
                :
                (isLoadFortran && isLoadBayes && isresultBayes && isresultFortran && <div>
                    <h4>Результаты оценки совместимости</h4>
                    <h5>Проверяемые лекарственные средства: { Array.isArray(resultBayes.drugs) && resultBayes.drugs.join(" ")}</h5>
                    <h5 className="mt-3">Результаты: </h5>
                    <ComputationResults compatibility={resultBayes.сompatibility_bayes} />
                    
                    <h5 className="mt-3">Риски побочных эффектов: </h5>
                    {!isRegex(resultBayes.сompatibility_bayes, "banned")&&<div className="mt-3">

                        
                        <div className="mt-3 mb-2 flex jc-sb ai-center">
                            <h6>Эффекты в результате взаимодействия</h6>

                            {/* <select name="sortSelectSE" >
                                {SelectedType.map(type => 
                                    <option key={type.id} value={type.value}>{type.title}</option>)
                                }
                            </select> */}
                        </div>

                        {/* Вывод побочек по риску появления */}
                        {!compareView && resultBayes.side_effects && resultBayes.side_effects.find(e=>e.сompatibility.trim()==="incompatible") &&
                            <CollapsList
                                title = "Высокий уровень риска появления побочных эффектов"
                                className="ComputationResults incompatible"  //default
                                type="riscs"
                                content= {resultBayes.side_effects.find(e=>e.сompatibility.trim()==="incompatible")?.effects} //side_effect[0].effects
                            />
                        }
                        {
                            compareView && compareWithFortran.find(e=>e.сompatibility.trim()==="incompatible") &&
                                <CollapsList
                                    title = "Высокий уровень риска появления побочных эффектов"
                                    className="ComputationResults incompatible"
                                    type="compare-riscs"
                                    content= {compareWithFortran.find(e=>e.сompatibility.trim()==="incompatible")?.compareData}
                                />
                        }
                        {!compareView && resultBayes.side_effects && resultBayes.side_effects.find(e=>e.сompatibility.trim()==="caution") &&
                            <CollapsList
                                title = "Средний уровень риска появления побочных эффектов"
                                className="ComputationResults caution"  //default
                                type="riscs"
                                content= {resultBayes.side_effects.find(e=>e.сompatibility.trim()==="caution")?.effects} //side_effect[0].effects
                            />
                        }
                        {
                            compareView && compareWithFortran.find(e=>e.сompatibility.trim()==="caution") &&
                                <CollapsList
                                    title = "Средний уровень риска появления побочных эффектов"
                                    className="ComputationResults caution"
                                    type="compare-riscs"
                                    content= {compareWithFortran.find(e=>e.сompatibility.trim()==="caution")?.compareData}
                                />
                        }

                         {!compareView && resultBayes.side_effects && resultBayes.side_effects.find(e=>e.сompatibility.trim()==="compatible") &&
                            <CollapsList
                                title = "Низкий уровень риска появления побочных эффектов"
                                className="ComputationResults compatible mt-2"  //default
                                type="riscs"
                                content= {resultBayes.side_effects.find(e=>e.сompatibility.trim()==="compatible")?.effects} //side_effect[0].effects
                            />
                        }
                        {
                            compareView && compareWithFortran.find(e=>e.сompatibility.trim()==="compatible") &&
                                <CollapsList
                                    title = "Низкий уровень риска появления побочных эффектов"
                                    className="ComputationResults compatible mt-2"
                                    type="compare-riscs"
                                    content= {compareWithFortran.find(e=>e.сompatibility.trim()==="compatible")?.compareData}
                                />
                        }

                        <div className="mt-3 mb-2 flex jc-sb ai-center">
                            <h6>Эффекты в результате действия лекарственного средства</h6>

                            {/* <select name="sortSelectFD" >
                                {SelectedType.map(type => 
                                    <option key={type.id} value={type.value}>{type.title}</option>)
                                }
                            </select> */}
                        </div>

                        { /*!compareView &&*/ resultBayes.SEFromDrug && resultBayes.SEFromDrug.map((serd, index) =>
                            <CollapsList
                                title = {serd.d_name}
                                className="ComputationResults default mb-3"
                                type="riscs"
                                content= {serd.effects}

                                key={index}
                            />

                        )}
                        {/* {
                            compareView && (compareDtaFromDrug.length>0) && compareDtaFromDrug.map((serd, index) =>
                                <CollapsList
                                    title = {serd.d_name}
                                    className="ComputationResults default mb-3"
                                    type="compare-riscs"
                                    content= {serd.effects}

                                    key={index}
                                />
                            )
                        } */}


                        <div className="flex jc-sb mt-3">
                            <button className="btn send-btn" onClick={CompareWhithFortranHandler}>{compareTitle}</button>
                            <button className="btn send-btn" onClick={ ShowGraphHandker }>Отобразить граф</button>
                        </div>
                    </div>}
                </div>)      
            ))
            }
        </main>
    </div>
    )
}