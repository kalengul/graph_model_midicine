import { useAppDispatch, useAppSelector} from '../../redux/hooks';
import {Form} from 'react-final-form'; //Field
import { ComputationInputForm } from "../form/computationInputForm/computationInputForm"

import { ComputationBayesValidator } from '../../components/computationBayesForm/computationBayesValidator';
import { iteractionFortran, iteractionBayes, IComputationBayes } from '../../redux/ComputationSlice';


export const ComputationBayesForm = () =>{
    const dispatch = useAppDispatch()
    const computationList = useAppSelector(state=>state.computation.computationList)

    const SendHandler = (value: IComputationBayes) =>{
        if(computationList.length!=0){
            const data: IComputationBayes = {drugs: computationList, humanData: value.humanData}
            dispatch(iteractionBayes(data))
            dispatch(iteractionFortran({drugs: computationList, humanData: "0"}))
        }
    }
    return(
        <div className='mt-4'>
            <Form 
                initialValues={{ humanData: 0, drugs: [] }}
                onSubmit={SendHandler}
                validate={(values)=>ComputationBayesValidator(values)}
            >
            {({ handleSubmit, submitting}) => (
            <form onSubmit={handleSubmit}>
                <ComputationInputForm
                    label = "Лекарственнные средства для расчета взаимодействия"
                    name = "drugs"
                    placeholder = "Введите лекарственные средства"
                ></ComputationInputForm>

                {/* Здесь будет формочка для человечечких данных*/}
    
                <button className='btn send-btn' disabled={submitting} >Расчитать взаимодействие</button>
            </form>
            )}
            </Form>
        </div>
    )
}