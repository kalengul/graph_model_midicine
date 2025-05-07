import { ReactNode } from "react";
import { createPortal } from "react-dom"

import "./modal.scss"

interface IModalPortalProps{
    children: ReactNode
}

export const ModalPortal = (props: IModalPortalProps) =>{
    return createPortal(
        <> 
            <div className="modalPortal"/>
            <div className=" flex jc-center">
                {props.children}
            </div>
        </>
        , document.body
    )
}