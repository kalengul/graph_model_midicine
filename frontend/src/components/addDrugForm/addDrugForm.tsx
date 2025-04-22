import {Form} from 'react-final-form';
import { Input } from "../form/input/input"
import {AddDrugValidator} from "./addDrugValidator"
import "./addDrugForm.scss"

import { useAppDispatch} from '../../redux/hooks';
import { addDrug } from '../../redux/DrugManageSlice';

interface ISendDrugData{
    drug_name: string,
}

export const AddDrugForm = () =>{
    const dispatch = useAppDispatch()

    const SendHandler =async (values: ISendDrugData)=>{
        console.log(values)
        dispatch(addDrug(values))
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
                validate={(values)=>AddDrugValidator(values)}
            >
            {({ handleSubmit, submitting}) => (
            <form onSubmit={handleSubmit}>
                <Input label="Название лекарственного средства" 
                    name = "drug_name"
                    id = "drug_name"
                    type = "text"
                    placeholder = "Введите название лекарственного средства"
                ></Input>

                <button className='btn send-btn' onClick={ScrollInto} disabled={submitting} >Добавить</button>
            </form>
            )}
            </Form>
        </div>
    )
}