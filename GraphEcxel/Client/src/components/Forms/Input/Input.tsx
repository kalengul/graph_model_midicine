import {Field} from 'react-final-form';

interface IInput {
    name: string,
    type: string,
    placeholder?: string,
    id?: string

    label?: string
}

function Input(props: IInput){

    return(
        <Field name={props.name} type={props.type} placeholder={props.placeholder} id={props.id}>
        {({ input, meta }) => (
            <div className="mb-4 form-group required" data-err={(meta.error || !meta.touched)? true: false}>
                <label htmlFor={props.id} className="form-label control-label">{props.label}</label>
                <input {...input} className={(meta.error && meta.touched) ? 'errBorder form-control' : 'form-control'}/>
                {meta.error && meta.touched && <span className='err'>{meta.error}</span>}
            </div>
        )}
        </Field>
    )

}

export default Input