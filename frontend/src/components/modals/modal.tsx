import {ModalPortal} from "./modalPortal"
import "./modal.scss"

interface IModalProps{
    isVisible: boolean;
    id: string;
    message: string;
    onClose: () => void;
    handler: () => void;

    className?: string;
}

export const Modal = (props: IModalProps) =>{
    if (!props.isVisible) {
        return null;
    }

    return(
        <ModalPortal>
            <div id={props.id} className={props.className ? `modal-body ${props.className}` : "modal-body"}>
                {props.message}
                <hr/>
                <div className="flex jc-sb">
                    <button className="btn send-btn" onClick={props.handler}>Удалить</button>
                    <button className="btn close-btn" onClick={props.onClose}>Отмена</button>
                </div>
            </div>
        </ModalPortal> 
    )
}