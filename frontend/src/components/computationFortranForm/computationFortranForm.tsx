import { useAppDispatch, useAppSelector} from '../../redux/hooks';
import {Form, Field} from 'react-final-form';
import { ComputationInputForm } from "../form/computationInputForm/computationInputForm"

import {ComputationFortranValidator} from "./computationFortranValidator"
import { iteractionFortran, IComputationFortran, iteractionMedscape } from '../../redux/ComputationSlice';

interface IHumanData{
  label: string,
  value: string | number,
}

// interface FormDataFortran{
//   humanData: string
// }

export const ComputationFortranForm = () =>{

    const HumanData: IHumanData[] = [
      {label: "Общий", value: 0}, //"rangbase.txt"},
      {label: "Мужчины до 65", value: 1 }, //"rangm1.txt"},
      {label: "Женщины до 65", value: 2 }, //"rangf1.txt"},
      {label: "Нормальный", value: 3 }, //"rangfreq.txt"},
      {label: "Мужчины после 65", value: 4}, // "rangm2.txt"},
      {label: "Женщины после 65", value: 5 }, //"rangf2.txt"},
    ]

    const dispatch = useAppDispatch()
    const computationList = useAppSelector(state=>state.computation.computationList)

    const SendHandler = (value: IComputationFortran) =>{
        if(computationList.length!=0){
          const data: IComputationFortran = {drugs: computationList, humanData: value.humanData}
          dispatch(iteractionFortran(data))
          dispatch(iteractionMedscape(computationList))
        }
      }
    return (
        <div className='mt-4'>
          <Form 
              onSubmit={SendHandler}
              validate={(values)=>ComputationFortranValidator(values)}
          >
          {({ handleSubmit, submitting}) => (
          <form onSubmit={handleSubmit}>
              <ComputationInputForm
                  label = "Лекартсвеннные средства для расчета взаимодействия"
                  name = "drugs"
                  placeholder = "Введите лекарственные средства"
              ></ComputationInputForm>

              <div className="mb-4 form-group required">
                <label className="form-label control-label">Выбирете дополнительную информацию о пациенте</label>

                {HumanData.map((humanData, index)=>
                  <div className='flex ai-center jc-start' key={index}>
                    <Field 
                      name="humanData"
                      component="input"
                      type="radio"
                      value={humanData.value}
                      className="me-2"></Field>
                    <label>{humanData.label}</label>
                  </div>
                )}
              </div>
    
              <button className='btn send-btn' disabled={submitting} >Расчитать взаимодействие</button>
          </form>
          )}
          </Form>
        </div>
      );
}