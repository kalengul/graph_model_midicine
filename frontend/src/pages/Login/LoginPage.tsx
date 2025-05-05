import { useNavigate } from 'react-router-dom';

import { LoginForm } from "../../components/loginForm/loginForm"
import { useAppSelector } from "../../redux/hooks"
import { useEffect } from 'react';

export const LoginPage = () =>{
    const navigate = useNavigate()
    const isAuth = useAppSelector(state=>state.auth.isAuthenticated)
    useEffect(()=>{
        if(isAuth) navigate("/")
    }, [isAuth, navigate])
    return(
    <div className="flex ai-center jc-center h-100 w-100">
        <div className="w-50"> 
            <h3>Вход в систему</h3>
            <LoginForm ></LoginForm>
        </div>
    </div>
    )
}