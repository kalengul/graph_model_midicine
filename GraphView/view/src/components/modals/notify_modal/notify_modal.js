import React, { useState, useEffect} from "react";

import './notify_modal.css'

export const NotifyModal = (props) => {
    const [isClosing, setIsClosing] = useState(false);

    useEffect(() => {
        if(props.isOpen){
            setIsClosing(true)
            const timer = setTimeout(() => {
                props.setIsOpet(false);
                return () => clearTimeout(timer);
            }, 2000);
        }
        else{
            setIsClosing(false);
            props.setIsOpet(false);
        }
    }, [props.isOpen, props.setIsOpet]); // Запускаем эффект при изменении props.isOpen

    return (
        <>
            {props.isOpen  &&
                <div className={`modal notify_modal temporary ${isClosing ? ' fade-out-2' : ""}`}>
                    <p>{props.text}</p>
                </div>
            }
        </>
        
    )
}