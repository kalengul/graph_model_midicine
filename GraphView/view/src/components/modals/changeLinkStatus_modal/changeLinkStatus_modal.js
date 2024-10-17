import React, {useState} from "react";
import { useDispatch, useSelector} from "react-redux";
import { changeVerifyNode } from '../../../redux/verifyGraphSlice';

import { Button } from "../../button/button";

import "./changeLinkStatus_modal.css"
import {numStatusLink} from "../../../functions/numerators";

export const ChangeLinkStatusModal = (props) => {
    const id = props.id
    const [isClosing, setIsClosing] = useState(false);
    const [newStatusLink, setNewStatusLink] = useState("");


    const CloseModal = () =>{
        setIsClosing(true)
        const timer = setTimeout(() => {
            props.setIsOpet(false);
            setIsClosing(false);
            return () => clearTimeout(timer);
        }, 500);
    }

    return (
        <>
        { props.isOpen ?
            <div className={`modal ls_modal flex jc-center align-center ${isClosing ? ' fade-out-1' : ""}`}>
                <div className="ls_modal_content">
                    <div className="flex jc-sb">
                        <h3>Текущее состояние: </h3>
                        <Button view="close" onClick={CloseModal}/>
                    </div>
                    <div className="change-container">
                        <label>Выберете новое состояние:</label>
                        <div>
                            <div className='flex radio-block' >
                                <input name = "statusLink" type='radio' value="0"/>
                                <label>{numStatusLink[0]}</label>
                            </div>

                            <div className='flex radio-block'>
                                <input name = "statusLink" type='radio' value="1"/>
                                <label>{numStatusLink[1]}</label>
                            </div>
                 
                            <div className='flex radio-block' >
                                <input name = "statusLink" type='radio' value="2" />
                                <label>{numStatusLink[2]}</label>
                            </div>                
                        </div>
                    </div>
                    <Button view="fill" lable = "Сохранить"/>
                </div>
            </div>
            : ""
        }
        </>
        
    )
}