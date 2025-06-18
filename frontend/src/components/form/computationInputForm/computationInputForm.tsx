import { useState, useRef, KeyboardEvent} from 'react';
import { Field } from 'react-final-form';


import { useAppDispatch, useAppSelector} from '../../../redux/hooks';
import {IComputationElem, removeComputationElem, addValue} from "../../../redux/ComputationSlice"
import { IDrugElem} from "../../../redux/DrugManageSlice"

import "./computationInputForm.scss"

interface IComputationInputFormProps{
    label: string,
    name: string,
    placeholder: string,
}

export const ComputationInputForm = (props: IComputationInputFormProps) =>{
    const dispatch = useAppDispatch()
    const drugsList = useAppSelector((state)=>state.drugManage.drugs)
    const computationList = useAppSelector ((state)=>state.computation.computationList)

    const [inputValue, setInputValue] = useState(''); // Текущее значение поля ввода
    const [showSuggestions, setShowSuggestions] = useState(false); // флаг видимости подсказок
    const [suggestions, setSuggestions] = useState<typeof drugsList>([]); // список подсказок 

    const inputRef = useRef<HTMLInputElement>(null);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        setInputValue(value);

        if (value.length >= 1){
            const filtered = drugsList.filter(d=> d.drug_name.toLocaleLowerCase().includes(value.toLocaleLowerCase()))
            //Добавляем фильтрацию, что ЛС нет в списке добавленных
            setSuggestions(filtered);
        }   else setSuggestions([])
    };

    const addNewComputationElem = (value: string) => {
        const existingDrug = drugsList.find(
          d => d.drug_name.toLocaleLowerCase() === value.toLocaleLowerCase()
        );
        console.log(existingDrug)
    
        if (existingDrug) {
          dispatch(addValue({title: "computationList", value: existingDrug}));
        }

        setInputValue('');
        setSuggestions([]);
        inputRef.current?.focus();
    };
    

    const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
        if ((e.key === 'Enter' || e.key === ',') && inputValue.trim()) { // Добавляем новое значение, если введен enter или ,
          e.preventDefault();
          addNewComputationElem(inputValue.trim());
        } else if (e.key === 'Backspace' && !inputValue && computationList.length > 0) {
          dispatch(removeComputationElem(computationList[computationList.length - 1].id));
        }
    };

    const selectSuggestion = (computationDrug: IDrugElem) => {
        dispatch(addValue({title: "computationList", value: computationDrug}));
        setInputValue('');
        setSuggestions([]);
        inputRef.current?.focus();
    };

    const removeExistingComputation = (id: string) => {
        dispatch(removeComputationElem(id));
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
                                placeholder={computationList.length === 0 ? props.placeholder : ''}
                            />

                            {showSuggestions && suggestions.length > 0 && (
                                <div  className="mt-1 suggestions-dropdown">
                                    {suggestions.map(suggestion => (
                                    <div
                                        key={suggestion.id}
                                        className="suggestion-item"
                                        onMouseDown={() => selectSuggestion(suggestion)}
                                    >
                                        <div className="suggestion-name">{suggestion.drug_name}</div>
                                    </div>
                                    ))}
                                </div>
                            )}


                            <div className='mt-1 mb-2'>
                                {computationList.map((computationElem: IComputationElem) => (
                                    <span key={computationElem.id} className={`mt-1 me-1 computation-badge dg-${computationElem.dg_id}`}>
                                        {computationElem.drug_name}
                                        <button
                                            type="button"
                                            className="computation-remove"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                removeExistingComputation(computationElem.id);
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