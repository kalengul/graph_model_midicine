import axios from 'axios'

import {Form} from 'react-final-form';
import { Input } from '../form/input/input';
import {ComputationMedScapeValidator, IComputationMedScapeData} from "./computationMedScapeValidator"


import { FieldRenderProps } from 'react-final-form';

interface Recipient {
    id: string;
    email: string;
  }пш

type RecipientsInputProps = FieldRenderProps<string[]> & {
    availableRecipients?: Recipient[];
  };

export const ComputationMedScapeForm = ()=>{
    const SendHandler = async (values: IComputationMedScapeData)=>{
        //window.alert(values.drug_name)
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
        <div>
            <Form 
                onSubmit={SendHandler}
                validate={(values)=>ComputationMedScapeValidator(values)}
            >
            {({ handleSubmit, submitting}) => (
            <form onSubmit={handleSubmit}>
                <Input label="Название побочного эффекта" 
                    name = "se_name"
                    id = "se_name"
                    type = "text"
                    placeholder = "Введите название побочного эффекта"
                ></Input>

                <button className='btn send-btn' onClick={ScrollInto} disabled={submitting} >Добавить</button>
            </form>
            )}
            </Form>
        </div>
    )
}