import { ComputationFortranForm } from "../../components/computationFortranForm/computationFortranForm"

import { ComputationResults } from "../../components/messageCards/computationResults/computationResults"

import { useAppSelector } from "../../redux/hooks"

export const ComputationFortran = () =>{
    const isresultFortran = useAppSelector(state=>state.computation.isresultFortran)
    const resultFortran = useAppSelector(state=>state.computation.resultFortran)
    return(
        <>
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
                    
                    {   resultFortran.side_effects.find(e=>e.сompatibility.trim()==="incompatible") &&
                        
                        <div className="ComputationResults incompatible">
                            {resultFortran.side_effects.find(e=>e.сompatibility.trim()==="incompatible")?.effects?.map((e, index)=>
                                <div className='flex jc-sb w-100 ps-3 pe-3' key={index}>
                                 <div>
                                     <span className='me-3'>{index+1}.</span> 
                                     <span>{e.se_name}</span>
                                 </div>
                                 <span>{e.rank}</span>
                             </div>
                            )}
                        </div>
                        
                    }

                    {   resultFortran.side_effects.find(e=>e.сompatibility.trim()==="caution") &&
                        
                        <div className="ComputationResults caution mt-2">
                            {resultFortran.side_effects.find(e=>e.сompatibility.trim()==="caution")?.effects?.map((e, index)=>
                                <div className='flex jc-sb w-100 ps-3 pe-3' key={index}>
                                 <div>
                                     <span className='me-3'>{index+1}.</span> 
                                     <span>{e.se_name}</span>
                                 </div>
                                 <span>{e.rank}</span>
                             </div>
                            )}
                        </div>
                        
                    }

                    {   resultFortran.side_effects.find(e=>e.сompatibility.trim()==="compatible") &&
                        
                        <div className="ComputationResults compatible mt-2">
                            {resultFortran.side_effects.find(e=>e.сompatibility.trim()==="compatible")?.effects?.map((e, index)=>
                                <div className='flex jc-sb w-100 ps-3 pe-3' key={index}>
                                 <div>
                                     <span className='me-3'>{index+1}.</span> 
                                     <span>{e.se_name}</span>
                                 </div>
                                 <span>{e.rank}</span>
                             </div>
                            )}
                        </div>
                        
                    }

                    <h5 className="mt-3">Комбинации лекарсвтенных средств: </h5>
                    
                    {   resultFortran.combinations.find(e=>e.сompatibility.trim()==="incompatible") &&
                        
                        <div className="ComputationResults incompatible">
                            {resultFortran.combinations.find(e=>e.сompatibility.trim()==="incompatible")?.drugs?.map((d, index)=>
                             <div className='flex jc-sb w-100 ps-3 pe-3' key={index}>
                                 <div>
                                     <span className='me-3'>{index+1}.</span> 
                                     <span>{d}</span>
                                 </div>
                             </div>
                            )}
                        </div>
                        
                    }

                    {   resultFortran.combinations.find(e=>e.сompatibility.trim()==="caution") &&
                        
                        <div className="ComputationResults caution mt-2">
                            {resultFortran.combinations.find(e=>e.сompatibility.trim()==="caution")?.drugs?.map((d, index)=>
                                <div className='flex jc-sb w-100 ps-3 pe-3' key={index}>
                                 <div>
                                     <span className='me-3'>{index+1}.</span> 
                                     <span>{d}</span>
                                 </div>
                             </div>
                            )}
                        </div>
                        
                    }

                    {   resultFortran.combinations.find(e=>e.сompatibility.trim()==="compatible") &&
                        <div className="ComputationResults compatible mt-2">
                            {resultFortran.combinations.find(e=>e.сompatibility.trim()==="compatible")?.drugs?.map((d, index)=>
                                <div className='flex jc-sb w-100 ps-3 pe-3' key={index}>
                                 <div>
                                     <span className='me-3'>{index+1}.</span> 
                                     <span>{d}</span>
                                 </div>
                             </div>
                            )}
                        </div>
                        
                    }
                    
                    <hr/>
                    <h4>Результаты оценки совместимости по MedScape</h4>
                    <div>
                    
                        <h5>Проверяемые лекарственные средства: { Array.isArray(resultFortran.drugs) && resultFortran.drugs.join(" ")}</h5>
                        <h5 className="mt-3">Результаты: </h5>

                        <ComputationResults compatibility={resultFortran.compatibility_medscape} />

                        <h5 className="mt-3">Примечание:</h5>
                        <p>{resultFortran.description}</p>
                    </div>
                    {/* 
                    

                    

                    <h5 className="mt-3">Примечание:</h5>
                    <p>{resultMedScape.description}</p> */}
                </div>
            }

        </>
    )
}