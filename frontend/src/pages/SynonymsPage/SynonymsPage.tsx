import { useEffect, useState } from 'react';
import { Nav } from '../../components/nav/nav';

import { useAppDispatch, useAppSelector } from '../../redux/hooks';
import {fetchSynonymGroupList, fetchSynonymList, changeIsChange, ISynItemUpdate} from "../../redux/SynonymsSlice"

import "./SynonymsPage.scss"

export const SynonymsPage = () =>{
    const dispatch = useAppDispatch()
    useEffect(()=>{
        dispatch(fetchSynonymGroupList())
    }, [dispatch])

    const symGroups = useAppSelector(state=>state.synonyms.SynonymGroupList)
    const synnonyms = useAppSelector(state=>state.synonyms.SynonymList)

    const getSynonymListHandler = (event: React.ChangeEvent<HTMLSelectElement>) =>{
        dispatch(fetchSynonymList(event.target.value))
    }

    const [updateList, setUpdateList] = useState<ISynItemUpdate[]>([])
    const [isBlockUpdateBtn, setIsBlockUpdateBtn] = useState<boolean>(true)
    const changeSynonymStatusHandler = (id: string, curentIsChange: boolean)=>{
        const updateItem: ISynItemUpdate | undefined = updateList.find((elem: ISynItemUpdate) =>elem.s_id === id)
        if(!updateItem) setUpdateList([...updateList, {s_id: id, is_changed: !curentIsChange}])
        else setUpdateList(updateList=>updateList.map((elem: ISynItemUpdate) =>
            elem.s_id===id ? { ...elem, is_changed: !curentIsChange} : elem 
        ))

        dispatch(changeIsChange(id))
        setIsBlockUpdateBtn(false)
    }

    return(
        <div className="flex">
            <Nav></Nav>
            <main className="ms-2 p-3 w-100">
                <h1>Синонимы</h1>
                <div className='mt-4'>
                    <label htmlFor="symGroups" className="form-label control-label">Выберете группу синонимов</label>
                    <select id="symGroups" onChange={getSynonymListHandler} className="form-select" aria-label="Default select example">
                        <option selected value="">Выберете группу</option>
                        {Array.isArray(symGroups) && symGroups.map((group)=>
                            <option value={group.sg_id} key={group.sg_id}>{group.sg_name}</option>
                        )}
                    </select>
                </div>

                <div className='mt-4 synList'>
                    { Array.isArray(synnonyms) && synnonyms.length>0 ? synnonyms.map((syn, index)=>
                        <div onClick={()=>changeSynonymStatusHandler(syn.s_id, syn.is_changed)} className={`flex jc-sb w-100 ps-3 pe-3 sunList-elem ${syn.is_changed ? "isChange": "no_isChange"}`} key={syn.s_id}>
                            <div>
                                <span className='me-3'>{index+1}.</span> 
                                <span>{syn.s_name}</span>
                            </div>
                        </div> 
                    ): <></>}
                </div>

                <button disabled={isBlockUpdateBtn}>Сохранить</button>

                

            </main>
        </div>
    )
}