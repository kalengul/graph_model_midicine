import { useEffect, useState } from 'react';
import { Nav } from '../../components/nav/nav';

import { useAppDispatch, useAppSelector } from '../../redux/hooks';
import {fetchSynonymGroupList, fetchSynonymList, updateSynonymList} from "../../redux/SynonymsSlice"

import "./SynonymsPage.scss"
import { SynonimGroupTypes } from '../../components/synonimGroupTypes/synonimGroupTypes';
import { SynCard } from '../../components/synCard/synCard';

export const SynonymsPage = () =>{
    const [isBlockUpdateBtn, setIsBlockUpdateBtn] = useState<boolean>(true)

    const symGroups = useAppSelector(state=>state.synonyms.SynonymGroupList)
    const synnonyms = useAppSelector(state=>state.synonyms.SynonymList)
    const updateList = useAppSelector(state=>state.synonyms.updateList)
    const synStatusList = useAppSelector(state=>state.synonyms.synStatusList)

    const SelectGr = useAppSelector(state=>state.synonyms.SelectGr)
    // console.log(SelectGr_id)
    // console.log(symGroups)

    const dispatch = useAppDispatch()
    useEffect(()=>{
        dispatch(fetchSynonymGroupList())
    }, [dispatch])

    useEffect(()=>{
        if (!updateList || updateList.length===0) setIsBlockUpdateBtn(true)
        else setIsBlockUpdateBtn(false)
    },[updateList])

    const getSynonymListHandler = (event: React.ChangeEvent<HTMLSelectElement>) =>{
        dispatch(fetchSynonymList(event.target.value))
    }

    const saveHandler = ()=>{
        dispatch(updateSynonymList())
    }

    const GetBgColorHandler = (st_id: string | undefined) : string =>{
        const status = synStatusList.find(st=>st.st_id===st_id)

        if(!status) return "#fff"
        else if(status.st_code === null) return "#fff"
        else return status.st_code
    }

    return(
        <div className="flex">
            <Nav></Nav>
            <main className="ms-2 p-3 w-100">
                <h1>Синонимы</h1>
                <div className='mt-3'>
                    <label htmlFor="symGroups" className="form-label control-label">Выберете группу синонимов</label>
                    <select id="symGroups" onChange={getSynonymListHandler} className="form-select" aria-label="Default select example">
                        <option selected value="">Выберете группу</option>
                        {Array.isArray(symGroups) && symGroups.map((group)=>
                            <option value={group.sg_id} key={group.sg_id}>{group.sg_name}</option>
                        )}
                    </select>
                </div>
                {SelectGr &&
                 <>
                    <div className='mt-3 flex jc-sb'>
                        <div className='synList me-5'>
                            <p className="h7">Группа {SelectGr.sg_name}</p>
                            
                            { Array.isArray(synnonyms) && synnonyms.length>0 ? synnonyms.map((syn, index)=>
                                <SynCard 
                                   key = {syn.s_id} id={syn.s_id} s_name={syn.s_name} index={index+1} bgColor={GetBgColorHandler(syn.st_id)}
                                ></SynCard>
                                // <div onClick={()=>changeSynonymStatusHandler(syn.s_id, syn.is_changed)} className={`flex jc-sb w-100 ps-3 pe-3 sunList-elem ${syn.is_changed ? "isChange": "no_isChange"}`} key={syn.s_id}>
                                //     <div>
                                //         <span className='me-3'>{index+1}.</span> 
                                //         <span>{syn.s_name}</span>
                                //     </div>
                                // </div> 
                            ): <></>}
                        </div>
                        <SynonimGroupTypes className='mt-3 me-4'/>
                    </div>

                    <button className='btn send-btn sm-btn mt-2' disabled={isBlockUpdateBtn} onClick={saveHandler}>Сохранить</button>
                </>
                }
            </main>
        </div>
    )
}