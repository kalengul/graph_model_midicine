import { LoginForm } from "../../components/loginForm/loginForm"

export const LoginPage = () =>{
    return(
    <div className="flex ai-center jc-center h-100 w-100">
        <div className="w-50"> 
            <h3>Вход в систему</h3>
            <LoginForm ></LoginForm>
        </div>
    </div>
    )
}