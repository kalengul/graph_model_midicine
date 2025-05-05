import {Form} from 'react-final-form';
import { Input } from "../form/input/input"

import { loginFormValidator } from './loginFormValidator';
import "./;oginForm.scss"


import { ILoginFormData, login } from "../../redux/AuthSlice"
import { useAppDispatch} from '../../redux/hooks';

interface LoginFormProps {
    className?: string,
}

export const LoginForm = (props: LoginFormProps) =>{
    const dispatch = useAppDispatch()

    const SendHandler =async (values: ILoginFormData)=>{
        dispatch(login(values))
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

    return(
        <div className={props.className}>
            <Form 
                onSubmit={SendHandler}
                validate={(values: ILoginFormData)=>loginFormValidator(values)}
            >
                 {({ handleSubmit, submitting}) => (
                    <form onSubmit={handleSubmit}>
                        <Input label="Логин" 
                            name = "username"
                            id = "username"
                            type = "text"
                            placeholder = "Введите ваш логин"
                            className='mb-1'
                        ></Input>
                        <Input label="Пароль" 
                            name = "password"
                            id = "password"
                            type = "password"
                            placeholder = "Введите ваш пароль"
                            className='mb-4'
                        ></Input>

                        <button className='btn send-btn border-send-btn w-100' onClick={ScrollInto} disabled={submitting} >Войти</button>
                    </form>
                 )}
            </Form>
        </div>
    )
}