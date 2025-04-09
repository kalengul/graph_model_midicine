import {useState, useEffect} from 'react'
import {useNavigate} from 'react-router-dom'
import axios from 'axios'

import {Field, Form} from 'react-final-form';
import Input from '../../components/Forms/Input/Input';

import Nav from '../../components/Nav/Nav'
import Button from '../../components/Button/Button'
import Select from '../../components/Forms/Select/Select';

function AddNewDrug() {
  const navigate = useNavigate();

  const [graphStates, setGraphStates] = useState([])
  const [file, setFile] = useState(null);

  useEffect(() => {
    try {
        axios({ 
            method: "GET", 
            url: "/api/getstates", 
        }).then((res)=>{
          //console.log(res.data)
          setGraphStates(res.data) //Доваление в useState
        })
    } catch (err) {console.error(err)}
  }, [])

  const SendHandler = async (values)=>{
    //window.alert(file)

    const data = new FormData();
    if(file){
      data.append('file', file);
    }

    data.append('drug_name', values.drug_name)
    data.append('status', values.status)

    try {
      await axios({ 
          method: "POST", 
          url: "/api/addnewdrug", 
          data,
          headers: { 'Content-Type': 'multipart/form-data'},
      }).then((res)=>{
        //console.log(res)
        alert(res.data.message)
        navigate('/') 
      })
      
    } catch (error) {
      console.log(error)
    }
    
    setFile(null)
    //navigate(`/graphs`);
  }

  // Обработчик изменения файла
  const fileChangeHandler = (e) => {
    setFile(e.target.files[0]); // Сохраняем выбранный файл в состояние
  };

  const validate = (values)=>{
    const errors={}

    if (!values.drug_name) errors.drug_name = "Пожалуйста введите название лекарственного средсва";

    if(values.graph_file){
      const fileParts: Array<string> = values.graph_file.split(".");
      if(fileParts[fileParts.length-1]!=="json") errors.graph_file = "Неверный формат схемы графа"
    }
    return errors;
  }

  const ScrollInto = () =>{
    let scrollElem = document.querySelector('[data-err=true]')
    if(scrollElem) {
        document.querySelector('[data-err=true]').scrollIntoView();
    }
  }

  return (
    <div className='flex'>
      <Nav isActive="addDrug"></Nav>
      <main className='flex jc-center'>
        <Form 
        onSubmit={SendHandler}
        validate={(values)=>validate(values)}
        >
        {({ handleSubmit, submitting}) => (
          <form onSubmit={handleSubmit}>
            <legend>Добавить новое лекарственное средство</legend>

            <Input name = "drug_name" 
              type='text' 
              id="drug_name"
              label='Введите название лекарственного средства'
            ></Input>

            <Select
              type='formSelect' 
              options={graphStates} 
              name='status' 
              id="disabledSelect"
              label="Состояние графа"
            ></Select>
            
            <div className="mb-4">
                <label htmlFor="graph_file" className="form-label control-label">
                  Добавьте файл с графом в формате .json
                </label>
                <input name = "graph_file" type="file"  id="graph_file" className='form-control' onChange={fileChangeHandler}/>
            </div>

            <Button typeBtn="Primary_btn" onClick={ScrollInto} disabled={submitting}>Добавить</Button>
          </form>
        )}
        </Form>
      </main>
    </div>
  )
}

export default AddNewDrug
