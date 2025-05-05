import {Form} from 'react-final-form';
import { Input } from "../form/input/input"
import {AddDrugGroupValidator} from "./addDrugGroupValidator"
import "./addDrugGroupForm.scss"

import { useAppDispatch} from '../../redux/hooks';
import { addDrugGroup, ISendDrugGroupData} from '../../redux/DrugGroupManageSlice';

export const AddDrugGroupForm = () =>{
    const dispatch = useAppDispatch()

    const SendHandler =async (values: ISendDrugGroupData)=>{
        dispatch(addDrugGroup(values.dg_name))
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
                validate={(values)=>AddDrugGroupValidator(values)}
            >
            {({ handleSubmit, submitting}) => (
            <form onSubmit={handleSubmit}>
                <Input label="Название группы лекарственных средств" 
                    name = "dg_name"
                    id = "dg_name"
                    type = "text"
                    placeholder = "Введите название группы лекарственных средств"
                    className='mb-4'
                ></Input>

                <button className='btn send-btn' onClick={ScrollInto} disabled={submitting} >Добавить</button>
            </form>
            )}
            </Form>
        </div>
    )
}