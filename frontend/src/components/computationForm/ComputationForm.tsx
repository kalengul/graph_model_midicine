import { useState } from 'react';
import { useAppDispatch, useAppSelector} from '../../redux/hooks';

import "./ComputationForm.scss"
import { Validation, IValidation } from './validation';

import { iteractionBayes, sendFormBayes, addDrugIds } from '../../redux/ComputationBayesSlice';
import { iteractionFortran, sendFormFortran, autoСompletionFortran} from '../../redux/ComputationFortranSlice';

type GenderType = 'man' | 'woman' | '';
interface IComputationFormProps {
    type: 'fortran' | 'bayes'
}

export const ComputationForm = (props: IComputationFormProps) =>{
    const dispatch = useAppDispatch()
    const drugsList = useAppSelector((state)=>state.drugManage.drugs)

    const [inputValueDrug, setInputValueDrug] = useState(''); // Текущее значение поля ввода
    const [suggestionsDrug, setSuggestionsDrug] = useState<typeof drugsList>([...drugsList]); // список подсказок
    const [showCkeckedDrug, setShowCheckedDrug] = useState<typeof drugsList>([]) //Список выдраннх ЛС для отображения
    const [checkedDrugIds, setCheckedDrugIds] = useState<string[]>([]) //Список выбранных ID ЛС
    const updateSuggestionsDrug = (value: string = '') =>{
    if (value.length >= 1) {
        const filtered = drugsList.filter(d => 
            d.drug_name.toLocaleLowerCase().includes(value.toLocaleLowerCase())
        );
        setSuggestionsDrug(filtered);
    } else {
        // Если поле пустое, показываем все лекарственные средства
        setSuggestionsDrug([...drugsList]);
    }
    }
    
    const serchSuggestionsDrugHandler = (e: React.ChangeEvent<HTMLInputElement>)=>{
    const value = e.target.value;

    setInputValueDrug(value)
    updateSuggestionsDrug(value);
    }

    const checkBoksDrugHandler = (e: React.ChangeEvent<HTMLInputElement>)=>{
        const { value, checked } = e.target;

        // Сохраняем id выбранных ЛС
        setCheckedDrugIds(prev => 
            checked 
                ? [...prev, value] 
                : prev.filter(id => id !== value)
        );

    // Обновляем список отображенния выбранных ЛС
    const drug = drugsList.find(e => e.id.toString() === value.toString())
    if(drug !== undefined){
        setShowCheckedDrug(prev=>
            checked
                ? [...prev, drug]
                : prev.filter(e => e.id.toString() !== value.toString())
        )
    }
    }

    const deleteDrugHandler = (e: React.MouseEvent<HTMLButtonElement>, id: string)=>{
        e.preventDefault();

        //удаляем выбранный id из списка
        if(checkedDrugIds.find(e => e.toString()===id.toString())) setCheckedDrugIds(checkedDrugIds.filter(e => e.toString()!==id.toString()))

        //удаляем ЛС из списка отображения
        if(showCkeckedDrug.find(e=>e.id.toString()===id.toString())) setShowCheckedDrug(showCkeckedDrug.filter(e=>e.id.toString()!==id.toString()))
    }

    const [gender, setGender] = useState<GenderType>('');

    const genderChangeHandle = (event: React.ChangeEvent<HTMLInputElement>) => {
        const value = event.target.value as GenderType;
        setGender(value);
    };

    const [age, setAge] = useState<number | ''>('');
    const ageChangeHandle = (event: React.ChangeEvent<HTMLInputElement>) => {
        const value = event.target.value;
        // Разрешаем пустую строку или числа
        if (value === '' || /^\d+$/.test(value)) {
            const numValue = value === '' ? '' : parseInt(value, 10);
            setAge(numValue);
        }
    };

    //Contraindication
    const contraindList = useAppSelector((state)=>state.contraindicationsManage.contraindications)
    const [inputValueContraind, setInputValueContraind] = useState(''); // Текущее значение поля ввода для противопоказаний
    const [suggestionsContraind, setSuggestionsContraind] = useState<typeof contraindList>([...contraindList]); // список подсказок противопоказаний
    const [showCkeckedContraind, setShowCheckedContraind] = useState<typeof contraindList>([]) //Список выдраннх противопоказаний для отображения
    const [checkedContraindIds, setCheckedContraindIds] = useState<string[]>([]) //Список выбранных ID противопоказаний

    const updateSuggestionsContraind = (value: string = '') =>{
        if (value.length >= 1) {
            const filtered = contraindList.filter(d => 
                d.cont_name.toLocaleLowerCase().includes(value.toLocaleLowerCase())
            );
            setSuggestionsContraind(filtered);
        } else {
            // Если поле пустое, показываем все лекарственные средства
            setSuggestionsContraind([...contraindList]);
        }
    }
    const serchSuggestionsContraindHandler = (e: React.ChangeEvent<HTMLInputElement>)=>{
        const value = e.target.value;

        setInputValueContraind(value)
        updateSuggestionsContraind(value);
    }

    const checkBoksContraindHandler = (e: React.ChangeEvent<HTMLInputElement>)=>{
        const { value, checked } = e.target;

        // Сохраняем id выбранных ЛС
        setCheckedContraindIds(prev => 
            checked 
                ? [...prev, value] 
                : prev.filter(id => id !== value)
        );

        // Обновляем список отображенния выбранных ЛС
        const contraind = contraindList.find(e => e.cont_id.toString() === value.toString())
        if(contraind !== undefined){
            setShowCheckedContraind(prev=>
                checked
                    ? [...prev, contraind]
                    : prev.filter(e => e.cont_id.toString() !== value.toString())
            )
        }
    }

    const deleteContraindHandler = (e: React.MouseEvent<HTMLButtonElement>, id: string)=>{
        e.preventDefault();

        //удаляем выбранный id из списка
        if(checkedContraindIds.find(e => e.toString()===id.toString())) setCheckedContraindIds(checkedContraindIds.filter(e => e.toString()!==id.toString()))

        //удаляем ЛС из списка отображения
        if(showCkeckedContraind.find(e=>e.cont_id.toString()===id.toString())) setShowCheckedContraind(showCkeckedContraind.filter(e=>e.cont_id.toString()!==id.toString()))
    }

    //Добавление файла
    const [selectedFile, setSelectedFile] = useState<File | null>(null);

    const checkFileHandler = (e: React.ChangeEvent<HTMLInputElement>) =>{
        const file = e.target.files?.[0];

        if (file) {
            setSelectedFile(file);

            //автозаполнение
            const autoComplete = dispatch(autoСompletionFortran(file)).unwrap()
            autoComplete.then(res =>{
                if(res.result.status === 200) {
                    if (res.data.age) setAge(res.data.age)
                    if (res.data.gender) setGender(res.data.gender)
                    if (res.data.cont_list) {
                        setCheckedContraindIds(res.data.cont_list.map(c=>c.toString())) //Заполняем список выбранных ID
                        //Заполняем противопоказания для отображения
                        setShowCheckedContraind([])
                        res.data.cont_list.map(elem => {
                            const cont = contraindList.find(e => e.cont_id.toString() === elem.toString())
                            if(cont) setShowCheckedContraind(prev => [...prev, cont])
                        })
                    }
                }
            })

        }
        else{
            setSelectedFile(null)
        }

        //вызов автозаполнения формы

    }

    //Отправка данных
    const SendDataHandler = (e: React.MouseEvent<HTMLButtonElement>) =>{
        e.preventDefault();

        const err: IValidation = Validation({drugs: checkedDrugIds, age: age, gender: gender, contrainds: checkedContraindIds, file: selectedFile})

        //Отправление формы
        if(err.isValid){
            if(props.type==='bayes'){
                const sendData: sendFormBayes = {
                    drugs: checkedDrugIds,
                    humanData: undefined
                }

                if(age !="" || gender != "" || checkedContraindIds.length>0) {
                    sendData.humanData = { age: undefined, gender: undefined, cont_list: undefined}
                    if(age !="") sendData.humanData.age = age.toString()
                    if(gender != "") sendData.humanData.gender = gender
                    if(checkedContraindIds.length>0) sendData.humanData.cont_list = checkedContraindIds
                }


                 const sendDataF: sendFormFortran = {
                    drugs: checkedDrugIds.map(drugId => Number(drugId)),
                    humanData: undefined
                }

                if(age !="" || gender != "" || checkedContraindIds.length>0) {
                    sendDataF.humanData = { age: undefined, gender: undefined, cont_list: undefined}
                    if(age !="") sendDataF.humanData.age = age
                    if(gender != "") sendDataF.humanData.gender = gender
                    if(checkedContraindIds.length>0) sendDataF.humanData.cont_list = checkedContraindIds
                }

                dispatch(addDrugIds(checkedDrugIds))
                dispatch(iteractionFortran(sendDataF))
                dispatch(iteractionBayes(sendData))
                
            } else if(props.type === 'fortran'){
                const sendData: sendFormFortran = {
                    drugs: checkedDrugIds.map(drugId => Number(drugId)),
                    humanData: undefined,
                    medCard: null
                }

                if(age !="" || gender != "" || checkedContraindIds.length>0) {
                    sendData.humanData = { age: undefined, gender: undefined, cont_list: undefined}
                    if(age !="") sendData.humanData.age = age
                    if(gender != "") sendData.humanData.gender = gender
                    if(checkedContraindIds.length>0) sendData.humanData.cont_list = checkedContraindIds
                }

                if(selectedFile) sendData.medCard = selectedFile

                dispatch(iteractionFortran(sendData))
            }
        }
    }

    const NosologyColorHandler = (nosology_id: string) =>{
        if (nosology_id == null) return "1"
        if (parseInt(nosology_id, 10) > 20) return "1"
        
        return nosology_id
    }

    return(
        <>
            <div className='mt-4 flex computationFormContainer'>
                {/* Блок для ввода списка ЛС */}
                <div className='me-4 computationFormBlock computationFormBlock-h30'>
                    <label className='form-label control-label lableCF'>Лекарственнные средства для расчета взаимодействия</label>
                    <div className='flex computationFormContainer-data'>
                        <div className='checkBlock me-3'>
                            <input onChange = {serchSuggestionsDrugHandler} value={inputValueDrug} name="drug-search" className=" checkBlock-search form-control mb-0" type="text" placeholder='Поиск ...'></input>
                            <div className='checkBlock-list'>
                                {suggestionsDrug && suggestionsDrug.map(drug=>(
                                    <div className='flex ai-start'>
                                        <input type="checkbox" checked={checkedDrugIds.includes(drug.id.toString())} onChange={checkBoksDrugHandler} key={drug.id} value={drug.id} className='me-2'/>
                                        <label>{drug.drug_name}</label>
                                    </div>
                                ))
                                }
                            </div>
                        </div> 
                        <div className='showBlock'>
                            <label className='form-label control-label'>Лекарственнные средства, выбранные для расчета:</label>
                            <div className='showBlock-list'>
                                {
                                    showCkeckedDrug && showCkeckedDrug.map(drug=>(
                                        
                                        <div className='flex ai-start mb-2'>
                                            <button type="button" className="btn-close me-2" aria-label="Close" onClick={(e) => deleteDrugHandler(e, drug.id)}></button>
                                            <span className={`dg-block dg-${NosologyColorHandler(drug.nosology_id)}`}> {drug.drug_name} </span>
                                        </div>
                                    ))
                                }
                            </div>
                        </div>
                    </div>
                </div>

                {/* Блок для ввода персональной информации и загрузки файла с мед картой */}
                <div className='computationFormBlock computationFormBlock-h50'>
                    <label className='form-label control-label lableCF'>Персональная информация пациента</label>
                    {/* Пол пациента */}
                    <div className='flex mb-2 ai-center'>
                        <label className=' control-label me-4'>Пол:</label>
                        <div className='flex'>
                            <div className='flex ai-center me-3'>
                                <input type="radio" value="man" name="gender" className='me-1' checked={gender === 'man'} onChange={genderChangeHandle}/>
                                <label>Мужской</label>
                            </div>
                            <div className='flex ai-center'>
                                <input type="radio" value="woman" name="gender" className='me-1' checked={gender === 'woman'} onChange={genderChangeHandle}/>
                                <label>Женский</label>
                            </div>
                        </div>
                    </div>
                    {/* Возраст пациента */}
                    <div className='flex ai-center mb-2'>
                        <label className='control-label me-4'>Возраст:</label>
                        <input className='form-control w-25' type="text" placeholder='Введите возраст' value={age === '' ? '' : age} onChange={ageChangeHandle}/>
                    </div>
                    {/* Противопоказания */}
                    <div className='mb-2 SuggestionsContainer'>
                        <label className='form-label control-label'>Сопутствующие заболевания (состояния):</label>
                        <div className='flex fd-row SuggestionsContainer-data' >
                            <div className='checkBlock me-3'>
                                <input onChange = {serchSuggestionsContraindHandler} value={inputValueContraind} name="drug-search" className=" checkBlock-search form-control mb-0" type="text" placeholder='Поиск ...'></input>
                                <div className='checkBlock-list'>
                                    {suggestionsContraind && suggestionsContraind.map(cont=>(
                                        <div className='flex ai-start'>
                                            <input type="checkbox" checked={checkedContraindIds.includes(cont.cont_id.toString())} onChange={checkBoksContraindHandler} key={cont.cont_id} value={cont.cont_id} className='me-2'/>
                                            <label>{cont.cont_name}</label>
                                        </div>
                                    ))
                                    }
                                </div>
                            </div> 
                            <div className='showBlock'>
                                <label className='form-label control-label'>Противопоказания, выбранные для расчета:</label>
                                <div className='showBlock-list'>
                                    {
                                        showCkeckedContraind && showCkeckedContraind.map(cont=>(
                                            
                                            <div className='flex ai-start mb-2'>
                                                <button type="button" className="btn-close me-2" aria-label="Close" onClick={(e) => deleteContraindHandler(e, cont.cont_id)}></button>
                                                <span> {cont.cont_name} </span>
                                            </div>
                                        ))
                                    }
                                </div>
                            </div>
                        </div>
                    </div>
                    {/* Загрузка медкарты */}
                    <div className='medcardBlock'>
                        <label className=' control-label'>Загрузить медицинскую карту:</label>
                        <input className="form-control" type="file" id="formFile" onChange={checkFileHandler}/>
                    </div>
                </div>
            
            </div>

            <button className='btn send-btn mt-3' onClick={SendDataHandler}>Рассчитать взаимодействие</button>
        </>
    )
}