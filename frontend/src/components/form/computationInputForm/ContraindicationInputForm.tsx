import { useState, useRef, KeyboardEvent} from 'react';
import { Field } from 'react-final-form';


import { useAppDispatch, useAppSelector} from '../../../redux/hooks';
import { removeContElem, addValue} from "../../../redux/ComputationSlice"
import { IContElem} from "../../../redux/ContraindicationsManageSlice"

import "./computationInputForm.scss"

interface IComputationInputFormProps{
    label: string,
    name: string,
    placeholder: string,
}

export const ContraindicationInputForm = (props: IComputationInputFormProps) =>{
    const dispatch = useAppDispatch()
    const contList = useAppSelector((state)=>state.contraindicationsManage.contraindications)
    const contChoiseList = useAppSelector ((state)=>state.computation.contList)
    // console.log(contChoiseList)

    const [inputValue, setInputValue] = useState(''); // Текущее значение поля ввода
    const [showSuggestions, setShowSuggestions] = useState(false); // флаг видимости подсказок
    const [suggestions, setSuggestions] = useState<typeof contList>([]); // список подсказок 

    const inputRef = useRef<HTMLInputElement>(null);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        setInputValue(value);

        if (value.length >= 1){
            const filtered = contList.filter(d=> d.cont_name.toLocaleLowerCase().includes(value.toLocaleLowerCase()))
            //Добавляем фильтрацию, что ЛС нет в списке добавленных
            setSuggestions(filtered);
        }   else setSuggestions([])
    };

    const addNewComputationElem = (value: string) => {
        const existingCont = contList.find(
          d => d.cont_name.toLocaleLowerCase() === value.toLocaleLowerCase()
        );
        console.log(existingCont)
    
        if (existingCont) {
          dispatch(addValue({title: "contList", value: existingCont}));
        }

        setInputValue('');
        setSuggestions([]);
        inputRef.current?.focus();
    };
    

    const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
        if ((e.key === 'Enter' || e.key === ',') && inputValue.trim()) { // Добавляем новое значение, если введен enter или ,
          e.preventDefault();
          addNewComputationElem(inputValue.trim());
        } else if (e.key === 'Backspace' && !inputValue && contChoiseList.length > 0) {
          dispatch(removeContElem(contChoiseList[contChoiseList.length - 1].cont_id));
        }
    };

    const selectSuggestion = (computationCont: IContElem) => {
        dispatch(addValue({title: "contList", value: computationCont}));
        setInputValue('');
        setSuggestions([]);
        inputRef.current?.focus();
    };

    const removeExistingComputation = (id: string) => {
        dispatch(removeContElem(id));
    };

    return(
        <Field name={props.name}>
            {({ input, meta }) => {
                 // Синхронизация с Redux
                const handleBlur = () => {
                    input.onBlur();
                    setTimeout(() => setShowSuggestions(false), 200);
                };

                return(
                    <div className="mb-4 сomputation-input-container">
                        <label className='form-label control-label'>{props.label}</label>
                        <div 
                            onClick={() => inputRef.current?.focus()}
                            className={`recipients-input ${meta.error && meta.touched ? 'is-invalid' : ''}`}
                        >

                            <input
                                ref={inputRef}
                                className='form-control recipients-input-field'
                                type="text"
                                value={inputValue}
                                onChange={handleInputChange}
                                onKeyDown={handleKeyDown}
                                onFocus={() => setShowSuggestions(true)}
                                onBlur={handleBlur}
                                placeholder={contChoiseList.length === 0 ? props.placeholder : ''}
                            />

                            {showSuggestions && suggestions.length > 0 && (
                                <div  className="mt-1 suggestions-dropdown">
                                    {suggestions.map(suggestion => (
                                    <div
                                        key={suggestion.cont_id}
                                        className="suggestion-item"
                                        onMouseDown={() => selectSuggestion(suggestion)}
                                    >
                                        <div className="suggestion-name">{suggestion.cont_name}</div>
                                    </div>
                                    ))}
                                </div>
                            )}


                            <div className='mt-1 mb-2'>
                                {contChoiseList.map((ContElem: IContElem) => (
                                    <span key={ContElem.cont_id} className={`mt-1 me-1 computation-badge`}>
                                        {ContElem.cont_name}
                                        <button
                                            type="button"
                                            className="computation-remove"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                removeExistingComputation(ContElem.cont_id);
                                            }}
                                        > × </button>
                                    </span>
                                ))}
                            </div>

                            
                        </div>
                    </div>
                )
            }}
        </Field>
    )
    
}