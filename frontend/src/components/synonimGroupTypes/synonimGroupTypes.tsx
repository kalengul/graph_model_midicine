import "./synonimGroupTypes.scss"
import { useEffect} from "react";
import { useAppDispatch, useAppSelector } from '../../redux/hooks';
import {fetchSynStatusList, updateSynStatusColor, changeColorStatus, chooseActiveStatus} from "../../redux/SynonymsSlice"

interface ISynonimGroupTypesProps{
 className?: string
}

export const SynonimGroupTypes = (props: ISynonimGroupTypesProps) =>{
    const dispatch = useAppDispatch()
    useEffect(()=>{
        dispatch(fetchSynStatusList())
    }, [dispatch])

    const synStatusList = useAppSelector(state=>state.synonyms.synStatusList)
    const activeStatus = useAppSelector(state=>state.synonyms.activeStatus)

    const changeColorHandler = (e: React.ChangeEvent<HTMLInputElement>, st_id: string) => {
        dispatch(changeColorStatus({st_id: st_id, newColor: e.target.value}))
    }

    const saveColorHandler = (e: React.ChangeEvent<HTMLInputElement>, st_id: string) =>{
        dispatch(updateSynStatusColor({newColor: e.target.value, st_id: st_id}))
    }

    return (
    <div className={props.className}>
        <p className="mb-3 h7">Группы синонимов</p>
        {synStatusList && (synStatusList.length>0) && synStatusList.map(synStatus =>
            <div key={synStatus.st_id} className="flex ai-center jc-sb mb-2">
                <span className={`me-2 st_name ${(activeStatus?.st_id == synStatus.st_id) && "isActive"}`} onClick={()=>dispatch(chooseActiveStatus(synStatus.st_id))}>{synStatus.st_name}</span>
                <input 
                    type="color" 
                    value={synStatus.st_code} 
                    className=" form-control form-control-sm form-control-color"
                    onChange = {(e)=>changeColorHandler(e, synStatus.st_id)}
                    onBlur={(e)=>saveColorHandler(e, synStatus.st_id)}
                />
            </div>
        )}
    </div>
    )
}