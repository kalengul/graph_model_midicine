import { useEffect } from "react"
import { ComputationFortranForm } from "../../components/computationFortranForm/computationFortranForm"

import { Nav } from '../../components/nav/nav';
import { ComputationResults } from "../../components/messageCards/computationResults/computationResults"
import { CollapsList } from "../../components/collapsList/collapsList";

import { useAppDispatch, useAppSelector } from "../../redux/hooks"
import { initResultFortran } from "../../redux/ComputationSlice"

export const ComputationFortran = () =>{
    const dispatch = useAppDispatch()

    useEffect(()=>{
        dispatch(initResultFortran())
    }, [dispatch])
    const isresultFortran = useAppSelector(state=>state.computation.isresultFortran)
    const resultFortran = useAppSelector(state=>state.computation.resultFortran)

    const isresultMedscape = useAppSelector(state=>state.computation.isresultMedscape)
    const resultMedscape = useAppSelector(state=>state.computation.resultMedscape)
    
    console.log(resultFortran)

    return(
        <div className="flex">
        <Nav></Nav>
        <main className="ms-2 p-3 w-100">
            <h1>Взаимодействие по Fortran</h1>

            <ComputationFortranForm/>
            <hr/>
            <h4>Результаты оценки совместимости</h4>
            {
                isresultFortran && <div>
                    <h5>Проверяемые лекарственные средства: { Array.isArray(resultFortran.drugs) && resultFortran.drugs.join(" ")}</h5>
                    <h5 className="mt-3">Результаты: </h5>
                    <ComputationResults compatibility={resultFortran.сompatibility_fortran} />

                    <h5 className="mt-3">Риски побочных эффектов: </h5>
                    
                    {resultFortran.side_effects && resultFortran.side_effects.find(e=>e.сompatibility.trim()==="incompatible") &&
                        <CollapsList 
                            className="ComputationResults incompatible"
                            type="riscs"
                            content= {resultFortran.side_effects.find(e=>e.сompatibility.trim()==="incompatible")?.effects}
                        />
                    }

                    { resultFortran.side_effects && resultFortran.side_effects.find(e=>e.сompatibility.trim()==="caution") &&
                        <CollapsList 
                            className="ComputationResults incompatible caution mt-2"
                            type="riscs"
                            content= {resultFortran.side_effects.find(e=>e.сompatibility.trim()==="caution")?.effects}
                        />
                    }

                    { resultFortran.side_effects &&  resultFortran.side_effects.find(e=>e.сompatibility.trim()==="compatible") &&
                        <CollapsList 
                            className="ComputationResults incompatible compatible mt-2"
                            type="riscs"
                            content= {resultFortran.side_effects.find(e=>e.сompatibility.trim()==="compatible")?.effects}
                        />
                    }

                    <h5 className="mt-3">Комбинации лекарсвтенных средств: </h5>
                    
                    {resultFortran.combinations &&   resultFortran.combinations.find(e=>e.сompatibility.trim()==="incompatible") &&
                        
                        <CollapsList 
                            className="ComputationResults incompatible"
                            type="drugs-combin"
                            content= {resultFortran.combinations.find(e=>e.сompatibility.trim()==="incompatible")?.drugs}
                        />

                        // <div className="ComputationResults incompatible">
                        //     {resultFortran.combinations.find(e=>e.сompatibility.trim()==="incompatible")?.drugs?.map((d, index)=>
                        //      <div className='flex jc-sb w-100 ps-3 pe-3' key={index}>
                        //          <div>
                        //              <span className='me-3'>{index+1}.</span> 
                        //              <span>{d}</span>
                        //          </div>
                        //      </div>
                        //     )}
                        // </div>
                        
                    }

                    { resultFortran.combinations &&  resultFortran.combinations.find(e=>e.сompatibility.trim()==="caution") &&
                        <CollapsList 
                            className="ComputationResults caution mt-2"
                            type="drugs-combin"
                            content= {resultFortran.combinations.find(e=>e.сompatibility.trim()==="caution")?.drugs}
                        />
                        // <div className="ComputationResults caution mt-2">
                        //     {resultFortran.combinations.find(e=>e.сompatibility.trim()==="caution")?.drugs?.map((d, index)=>
                        //         <div className='flex jc-sb w-100 ps-3 pe-3' key={index}>
                        //          <div>
                        //              <span className='me-3'>{index+1}.</span> 
                        //              <span>{d}</span>
                        //          </div>
                        //      </div>
                        //     )}
                        // </div>
                        
                    }

                    { resultFortran.combinations &&   resultFortran.combinations.find(e=>e.сompatibility.trim()==="compatible") &&
                        <CollapsList 
                            className="ComputationResults compatible mt-2"
                            type="drugs-combin"
                            content= {resultFortran.combinations.find(e=>e.сompatibility.trim()==="compatible")?.drugs}
                        />
                        // <div className="ComputationResults compatible mt-2">
                        //     {resultFortran.combinations.find(e=>e.сompatibility.trim()==="compatible")?.drugs?.map((d, index)=>
                        //         <div className='flex jc-sb w-100 ps-3 pe-3' key={index}>
                        //          <div>
                        //              <span className='me-3'>{index+1}.</span> 
                        //              <span>{d}</span>
                        //          </div>
                        //      </div>
                        //     )}
                        // </div>
                        
                    }
                    
                    <hr/>
                    <h4>Результаты оценки совместимости по MedScape</h4>
                    {isresultMedscape &&
                        Array.isArray(resultMedscape) && resultMedscape.map(res=>
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
                    {/* 
                    

                    

                    <h5 className="mt-3">Примечание:</h5>
                    <p>{resultMedScape.description}</p> */}
                </div>
            }

        </main>
        </div>
    )
}