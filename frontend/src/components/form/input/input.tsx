import {Field} from 'react-final-form';
import './input.scss'

interface IInputProps{
    label: string,
    name: string,
    id: string,
    type: string,
    placeholder: string
    className?: string
}

export const Input=(props: IInputProps)=>{
    const classes=`${props.className ? props.className: ""} form-group required `
    return(
        <Field name={props.name} type={props.type} placeholder={props.placeholder} id={props.id}>
        {({ input, meta }) => (
            <div className={classes} data-err={(meta.error || !meta.touched)? true: false}>
                <label htmlFor={props.id} className="form-label control-label">{props.label}</label>
                <input {...input} className={(meta.error && meta.touched) ? 'errBorder form-control' : 'form-control'}/>
                {meta.error && meta.touched && <span className='err'>{meta.error}</span>}
            </div>
        )}
        </Field>
    )
}