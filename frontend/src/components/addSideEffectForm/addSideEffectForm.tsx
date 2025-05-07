import {Form} from 'react-final-form';
import { Input } from "../form/input/input"
import {AddSideEffectValidator} from "./addSideEffectValidator"
import "./addSideEffectForm.scss"

import { useAppDispatch } from '../../redux/hooks';
import {ISendSideEffectData, addSideEffect} from '../../redux/SideEffectManageSlice'

export const AddSideEffectForm = () =>{
    const dispatch = useAppDispatch()

    const SendHandler =async (values: ISendSideEffectData)=>{
        dispatch(addSideEffect(values))
    }

    const ScrollInto = () =>{
        const scrollElem = document.querySelector('[data-err=true]')
        if(scrollElem) {
            scrollElem.scrollIntoView({ 
                behavior: 'smooth',  // Добавляем плавную прокрутку
                block: 'nearest'
            });
        }
    }

    return (
        <div>
            <Form 
                onSubmit={SendHandler}
                validate={(values)=>AddSideEffectValidator(values)}
            >
            {({ handleSubmit, submitting}) => (
            <form onSubmit={handleSubmit}>
                <Input label="Название побочного эффекта" 
                    name = "se_name"
                    id = "se_name"
                    type = "text"
                    placeholder = "Введите название побочного эффекта"
                    className='mb-4'
                ></Input>

                <button className='btn send-btn' onClick={ScrollInto} disabled={submitting} >Добавить</button>
            </form>
            )}
            </Form>
        </div>
    )
}
