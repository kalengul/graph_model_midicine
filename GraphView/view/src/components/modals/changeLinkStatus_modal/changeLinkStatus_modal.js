import React from "react";
import { useDispatch, useSelector} from "react-redux";
import { changeVerifyNode } from '../../../redux/verifyGraphSlice';

import { Button } from "../../button/button";

import "./changeLinkStatus_modal.css"

export const ChangeLinkStatusModal = (props) => {
    const id = props.id

    return (
        <div className="ls_modal flex jc-center align-center">
            <div className="ls_modal_content">
                <div className="flex jc-sb">
                    <h3>Текущее состояние: </h3>
                    <Button view="close"/>
                </div>
                <div>
                    <label>Выберете новое состояние:</label>
                </div>
                <Button view="fill" lable = "Сохранить"/>
            </div>
        </div>
    )
}