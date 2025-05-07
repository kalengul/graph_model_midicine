
import { ILoginFormData, ILoginFormDataError } from "../../redux/AuthSlice"

export const loginFormValidator = (values: ILoginFormData) =>{
    const errors: ILoginFormDataError = {}

    if (!values.username) errors.username = "Пожалуйста введите логин";
    if (!values.password) errors.password = "Пожалуйста введите пароль";

    return errors
}