import { useEffect } from "react";

interface IModalNotification{
    type: string |'success' | 'error';
    message: string;
    onClose: () => void;
}

export const ModalNotification = (props: IModalNotification) =>{
    useEffect(() => {
        const timer = setTimeout(() => {
            props.onClose();
        }, 3000); // Автоматическое закрытие через 3 секунды

        return () => clearTimeout(timer);
    }, [props.onClose]);

    return(
        <div className={`notification ${props.type}`}>
            <div className="notification-content">
                <span>{props.message}</span>
                <button className="notif-btn" onClick={props.onClose}>×</button>
            </div>
        </div>
    )
}