import React from "react";
import "./button.css"

import {ReactComponent as Trash} from "../../static/img/Trash.svg"
import {ReactComponent as FileDownload} from "../../static/img/FileDownload.svg"

export const Button = (props) => {
    let classesName = "btn"
    if (props.view === "fill") classesName+=" btn-fill"
    if (props.view === "unfill") classesName+=" btn-unfill"

    switch (props.view) {
        case "delete":
            return ( <Trash className="btn-icon" onClick = {props.onClick}/> )

        case "download":
            return ( <FileDownload className="btn-icon" onClick = {props.onClick}/> ) 
        
        default:
            return(
                <button type={props.type} className={classesName} onClick = {props.onClick} disabled = {props.disabled}>{props.lable}</button>
            )
    }
}