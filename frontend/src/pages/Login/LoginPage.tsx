import { useNavigate } from 'react-router-dom';

import { LoginForm } from "../../components/loginForm/loginForm"
// import { HelloCard } from './HelloCard/HelloCard';
import { useAppSelector } from "../../redux/hooks"
import { useEffect } from 'react';

import "./loginPage.scss"

export const LoginPage = () =>{
    const navigate = useNavigate()
    const isAuth = useAppSelector(state=>state.auth.isAuthenticated)

    useEffect(()=>{
        if(isAuth) navigate("/")
    }, [isAuth, navigate])

    return(
    <main className='loginPage flex jc-sb'>
        <div className="flex ai-center jc-center h-100 w-50">
            <div className="login-main w-75"> 
                <h2>Вход в систему</h2>
                <LoginForm ></LoginForm>
            </div>
        </div>

        <div className='loginContent flex jc-center w-50'>
            {/* <HelloCard>
                <p className='m-0'>Добро пожаловать в систему оценки рисков </p>
                <p className='m-0 logo'>ТОШ</p>
            </HelloCard> */}
            <div>
                <p className='m-0'>Добро пожаловать в систему оценки рисков </p>
                <p className='m-0 logo'>ТОШ</p>
            </div>
        </div>
    </main>
    )
}