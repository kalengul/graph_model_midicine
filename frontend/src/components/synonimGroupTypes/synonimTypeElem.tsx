import {memo} from "react"

interface ISynonimTypeElem{
    st_id: string
    st_name: string
    st_code: string
}

export const SynonimTypeElem = memo((props: ISynonimTypeElem) =>{
    return (  
        <div key={props.st_id} className="flex ai-center jc-sb mb-2">
            <span className={`me-2 st_name ${(activeStatus?.st_id == props.st_id) && "isActive"}`} onClick={()=>dispatch(chooseActiveStatus(props.st_id))}>{props.st_name}</span>
            <input 
                type="color" 
                value={props.st_code} 
                className=" form-control form-control-sm form-control-color"
                onChange = {(e)=>changeColorHandler(e, props.st_id)}
                onBlur={(e)=>saveColorHandler(e, props.st_id)}
            />
        </div>)
})