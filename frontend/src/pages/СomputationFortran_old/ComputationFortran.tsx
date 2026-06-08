import { useEffect, useState } from "react"

import { ComputationForm } from "../../components/computationForm/ComputationForm";
import { ComputationResults } from "../../components/messageCards/computationResults/computationResults"
import { CollapsList } from "../../components/collapsList/collapsList";

import { useAppDispatch, useAppSelector } from "../../redux/hooks"
import { initStates } from "../../redux/ComputationFortranSlice"
import { LoadBar } from "../../components/loadBar/loadBar";

export const ComputationFortran = () =>{
    const dispatch = useAppDispatch()

    useEffect(()=>{
        dispatch(initStates())
    }, [dispatch])

    const isLoad = useAppSelector(state=>state.computationFortran.isLoad)
    const resultFortran = useAppSelector(state=>state.computationFortran.resultFortran)
    const isResultFortran = useAppSelector(state=>state.computationFortran.isresultFortran);
    const errMessage = useAppSelector(state=>state.computationFortran.errMessage)
    const isSend = useAppSelector(state=>state.computationFortran.isSend)

    const [isVisibleRick, setIsVisibleRick] = useState(false)
    const [visibleTytle, setVisibleTytle] = useState("Показать объяснение")

    const VisibleRanksHandler = () =>{
        if(isVisibleRick) setVisibleTytle("Показать объяснение")
        else setVisibleTytle("Скрыть объяснение")
        setIsVisibleRick(!isVisibleRick)
    }

    return(
        
        <main className="ms-2 p-3 w-100">
            <h1>Взаимодействие по Fortran</h1>

            <ComputationForm type="fortran"/>

            {/* <ComputationFortranForm/> */}
            <hr/>

            {isSend && <>
            <h4>Результаты оценки совместимости</h4>
            {
                !isLoad ? <LoadBar className="mt-4"/>
                :
                ((!isResultFortran) ? <p>{errMessage && errMessage}</p> 
                    :
                    <div>
                        <h5>Проверяемые лекарственные средства: {Array.isArray(resultFortran.drugs) && resultFortran.drugs.join(" ")}</h5>
                        <h5 className="mt-3">Результаты: </h5>
                        <ComputationResults compatibility={resultFortran.compatibility_fortran} />
                        {resultFortran.compatibility_fortran !== "banned" && resultFortran.compatibility_fortran !== "banned-contraindications" &&
                        <>
                            <h5 className="mt-3">Риски побочных эффектов: </h5>
                        
                            {resultFortran.side_effects && resultFortran.side_effects.find(e=>e.compatibility.trim()==="incompatible") &&
                                <CollapsList
                                    title = "Высокий уровень риска появления побочных эффектов"
                                    className="ComputationResults incompatible"
                                    type="riscs"
                                    content= {resultFortran.side_effects.find(e=>e.compatibility.trim()==="incompatible")?.effects}
                                    visibleRisks = {isVisibleRick}
                                />
                            }

                            { resultFortran.side_effects && resultFortran.side_effects.find(e=>e.compatibility.trim()==="caution") &&
                                <CollapsList 
                                    title = "Средний уровень риска появления побочных эффектов"
                                    className="ComputationResults incompatible caution mt-2"
                                    type="riscs"
                                    content= {resultFortran.side_effects.find(e=>e.compatibility.trim()==="caution")?.effects}
                                    visibleRisks = {isVisibleRick}
                                />
                            }

                            { resultFortran.side_effects &&  resultFortran.side_effects.find(e=>e.compatibility.trim()==="compatible") &&
                                <CollapsList
                                    title = "Низкий уровень риска появления побочных эффектов" 
                                    className="ComputationResults incompatible compatible mt-2"
                                    type="riscs"
                                    content= {resultFortran.side_effects.find(e=>e.compatibility.trim()==="compatible")?.effects}
                                    visibleRisks = {isVisibleRick}
                                />
                            }

                           
                            
                            {isVisibleRick &&
                                <div className="mt-2">
                                    <h6>Коэффициенты побочных эффектов:</h6>
                                    { resultFortran.SEFromDrug && resultFortran.SEFromDrug.map((serd, index) =>
                                        <CollapsList
                                            title = {serd.d_name}
                                            className="ComputationResults default mb-3"
                                            type="riscs"
                                            content= {serd.effects}
                                            key={index}
                                            visibleRisks={isVisibleRick}
                                        />)
                                    }
                                </div>
                            }
                            <button className="btn send-btn mt-1" onClick={VisibleRanksHandler}>{visibleTytle}</button>

                            <h5 className="mt-3">Дополнительные лекарственные средства: </h5>
                    
                            {resultFortran.combinations &&   resultFortran.combinations.find(e=>e.compatibility.trim()==="incompatible") &&
                                
                                <CollapsList
                                    title = "Лекарственные средства, запрещенные с данной комбинацией"
                                    className="ComputationResults incompatible"
                                    type="drugs-combin"
                                    content= {resultFortran.combinations.find(e=>e.compatibility.trim()==="incompatible")?.drugs}
                                    visibleRisks = {isVisibleRick}
                                />
                            }

                            { resultFortran.combinations &&  resultFortran.combinations.find(e=>e.compatibility.trim()==="caution") &&
                                <CollapsList
                                    title = "Лекарственные средства, которые добавлять с осторожностью:"
                                    className="ComputationResults caution mt-2"
                                    type="drugs-combin"
                                    content= {resultFortran.combinations.find(e=>e.compatibility.trim()==="caution")?.drugs}
                                    visibleRisks = {isVisibleRick}
                                />
                            }

                            { resultFortran.combinations &&   resultFortran.combinations.find(e=>e.compatibility.trim()==="compatible") &&
                                <CollapsList 
                                    title = "Лекарственные средства, которые можно добавлять к комбинации:"
                                    className="ComputationResults compatible mt-2"
                                    type="drugs-combin"
                                    content= {resultFortran.combinations.find(e=>e.compatibility.trim()==="compatible")?.drugs}
                                    visibleRisks = {isVisibleRick}
                                />
                            }
                        </>}
                    </div>
                ) 
            }
            </>}

        </main>
    )
}