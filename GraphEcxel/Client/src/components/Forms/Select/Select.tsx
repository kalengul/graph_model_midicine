import { useDispatch} from 'react-redux';
import {addStatusChange} from '../../../redux/DrugsSlice'

import {Field} from 'react-final-form';

import "./selesct.scss"

interface ISelect{
    type: string, //tableSelect, formSelect
    options: [],
    id:string,

    activeOption?: string,

    name?: string,
    label?: string,
}

function Select(props: ISelect) {
    const dispatch = useDispatch()
    const onChangeHandler=(e)=>{
        dispatch(addStatusChange({drug_id: e.target.id, newStatus: e.target.value}));
    }

    switch (props.type) {
        case "tableSelect":
            return(
                <select id={props.id} className="form-select table-select" aria-label="Default select example" onChange={onChangeHandler}>
                    <option selected={props.activeOption == undefined || props.activeOption == null }></option>
                    {Array.isArray(props.options) && props.options.map((state, index)=>
                        <option value={state} key={index} selected={state==props.activeOption}>{state}</option>
                    )}
                </select>
            )
        case "formSelect":
            return(
                <Field name={props.name || ""} id={props.id}>
                {({ input, meta }) => (
                  <div className="mb-4">
                    <label htmlFor={props.id} className="form-label">Состояние графа</label>
                    <div data-err={(meta.error || !meta.touched)? true: false}>
                      <select {...input}  className={(meta.error && meta.touched) ? 'errBorder form-select select-sh-m' : 'form-select select-sh-m'}>
                        <option selected>Выбирете состояние</option>
                        {Array.isArray(props.options) && props.options.map((state, index)=>
                          <option value={state} key={index}>{state}</option>
                        )}
                      </select>
                    </div>
                    {meta.error && meta.touched && <span className='err'>{meta.error}</span>}
                  </div>
                )}
                </Field>
            )
        default:
            return <></>;
    }
}

export default Select