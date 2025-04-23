
import { useAppDispatch, useAppSelector} from '../../redux/hooks';
import {Form} from 'react-final-form';
import { ComputationInputForm } from "../form/computationInputForm/computationInputForm"

import {ComputationMedScapeValidator} from "./computationMedScapeValidator"

import { iteractionMedscape } from '../../redux/ComputationSlice';


export const ComputationMedScapeForm = () => {
  const dispatch = useAppDispatch()
  const computationList = useAppSelector(state=>state.computation.computationList)

  const SendHandler = () =>{
    dispatch(iteractionMedscape(computationList))
  }

  return (
    <div className='mt-4'>
      <Form 
          onSubmit={SendHandler}
          validate={(values)=>ComputationMedScapeValidator(values)}
      >
      {({ handleSubmit, submitting}) => (
      <form onSubmit={handleSubmit}>
          <ComputationInputForm
              label = "Лекартсвеннные средства для расчета взаимодействия"
              name = "drug_list"
              placeholder = "Введите лекарственные средства"
          ></ComputationInputForm>

          <button className='btn send-btn' disabled={submitting} >Расчитать взаимодействие</button>
      </form>
      )}
      </Form>
    </div>
  );
};