interface IValidationData {
    drugs: string[]
    age: number | ''
    gender: string,
    contrainds: string[]
    file: File | null
}

interface IError {
    name: string
    message: string
}

export interface IValidation{
    isValid: boolean,
    err: IError[]
}

export const Validation = (data: IValidationData) : IValidation =>{
    const isValid: IValidation = {isValid: true, err: []}

    //Валидация списка ЛС
    if(data.drugs.length<1) {
        isValid.isValid = false
        isValid.err.push({name: 'drugs', message: "Не заполнено обязательное поле"})
    }

    //Валидация возраста
    if(data.age !== undefined && data.age !== ''){
        const ageNum = typeof data.age === 'number' ? data.age : parseInt(data.age, 10);
        if (isNaN(ageNum) || ageNum < 0 || ageNum > 120) {
            isValid.isValid = false
            isValid.err.push({name: 'age', message: "Возраст должен быть от 0 до 120 лет"})
        }
    }

    //Валидация пола
    const validGenders = ['man', 'woman']
    if(data.gender !== '' && !validGenders.includes(data.gender)){
        isValid.isValid = false
        isValid.err.push({name: 'gender', message: "Ошибка при определении пола"})
    }

    return isValid
}