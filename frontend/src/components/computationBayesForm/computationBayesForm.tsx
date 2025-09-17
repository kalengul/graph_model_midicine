import { useAppDispatch, useAppSelector} from '../../redux/hooks';
import {Form} from 'react-final-form'; //Field
import { ComputationInputForm } from "../form/computationInputForm/computationInputForm"
import { ContraindicationInputForm } from '../form/computationInputForm/ContraindicationInputForm';

import { ComputationBayesValidator } from '../../components/computationBayesForm/computationBayesValidator';
import { iteractionFortran, iteractionBayes, IComputationBayes } from '../../redux/ComputationSlice';
//import { ComputationForm } from '../form/computationInputForm/computationForm_v2';




export const ComputationBayesForm = () =>{
    const dispatch = useAppDispatch()
    const computationList = useAppSelector(state=>state.computation.computationList)
    const contList = useAppSelector(state=> state.computation.contList)

    const SendHandler = (value: IComputationBayes) =>{
        if(computationList.length!=0){
            const humanData = value.humanData
            // console.log(humanData)
            // console.log(contList)
            if(contList && contList.length>0){
                if(!humanData?.cont_list) humanData.cont_list = []
                contList.forEach(cont=> humanData?.cont_list?.push(cont.cont_id))

                // console.log(humanData)
            }
            const data: IComputationBayes = {drugs: computationList, humanData: humanData}
            dispatch(iteractionBayes(data))
            dispatch(iteractionFortran({drugs: computationList, humanData: "0"}))
        }
    }
    return(
        <div className='mt-4'>
            <Form 
                initialValues={{ humanData: {age: undefined, gender: undefined, cont_list: undefined}, drugs: [] }}
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

                <ContraindicationInputForm
                    label = "Противопоказания"
                    name = "const"
                    placeholder = "Введите противопоказание"
                ></ContraindicationInputForm>
                {/* <ComputationForm
                    label = "Лекарственнные средства для расчета взаимодействия 2"
                    name = "drugs"
                    placeholder = "Введите лекарственные средства"
                    contentType ="drugs"
                    content={drugsList}
                    computationList={computationList}
                ></ComputationForm> */}

                {/* Здесь будет формочка для человечечких данных*/}
    
                <button className='btn send-btn' disabled={submitting} >Расчитать взаимодействие</button>
            </form>
            )}
            </Form>
        </div>
    )
}