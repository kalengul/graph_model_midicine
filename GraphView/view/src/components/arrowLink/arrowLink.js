import React from "react";

import ArrowLeft from "../../static/img/ArrowLeft.svg"
import "./arrowLink.css"

export const ArrowLink = (props) =>{
    return (
        <div className={`${props.className}+ arrow`} onClick = {props.onClick}>
            <img className="arrow-small" alt="arrow" src={ArrowLeft}/>
            <p>{props.title}</p>
        </div>
    )
}