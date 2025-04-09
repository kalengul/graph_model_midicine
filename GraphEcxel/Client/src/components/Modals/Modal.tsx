import {useState} from 'react'
import { Modal as BootstrapModal , Button} from 'react-bootstrap';

import "./Modal.scss"

const Modal = (props) => {
    return (
        <BootstrapModal id={props.id} show={props.show} onHide={props.handleClose}>
            <BootstrapModal.Header closeButton>
                <BootstrapModal.Title>{props.title}</BootstrapModal.Title>
            </BootstrapModal.Header>
            <BootstrapModal.Body>{props.children}</BootstrapModal.Body>
            <BootstrapModal.Footer>
                <div className="btn-div-modal flex jc-sb">
                    <Button variant="secondary" onClick={props.handleClose}>
                        Отмена
                    </Button>
                    <Button variant="primary" onClick={props.onConfirm}>
                        Удалить
                    </Button>
                </div>
            </BootstrapModal.Footer>
        </BootstrapModal>
    )
}


export default Modal