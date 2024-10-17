import React, { useState, useEffect} from "react";

import {NotifyModal} from "./notify_modal/notify_modal"
import { ChangeLinkStatusModal } from "./changeLinkStatus_modal/changeLinkStatus_modal";
 
import './modal.css'

export const Modal = (props) => {
    switch (props.type) {
        case "notify":
            return (
                <NotifyModal text="Запись добавлена успешно!" isOpen={props.isOpen} setIsOpet={props.setIsOpet}/>
            )
        case "changeLinkStatus":
            return(
                <ChangeLinkStatusModal isOpen={props.isOpen} setIsOpet={props.setIsOpet} id={props.id}/>
            )   
    
        default:
            break;
    }
}