import {useNavigate} from 'react-router-dom'
import {useSelector, useDispatch} from 'react-redux';
import axios from 'axios'
import { saveAs } from 'file-saver';

import {initStatusChange} from '../../redux/DrugsSlice'

import Nav from '../../components/Nav/Nav'
import Table from '../../components/Table/Table'
import Button from '../../components/Button/Button'
import StatisticGrugs from '../../components/StatisticGrugs/StatisticGrugs'

import plus from "../../assets/plus.svg"
import filter from "../../assets/filter.svg"

function MarkForInstructions() {
    const dispatch = useDispatch()
    const navigate = useNavigate();
    const navigate_AddDrug = () => { 
        //console.log('/add_drug')
        navigate('/add_drug') 
    };

    const drugs_changes = useSelector(state=>state.drugs.statusChanges)
    // console.log(drugs_changes)
    const drugs = useSelector(state=>state.drugs.drugs)

    const saveChangesHandler= async ()=>{
        const data = {data: drugs_changes}
        try {
            await axios({ 
                method: "POST", 
                url: "/api/update", 
                data,
                headers: { 'Content-Type': 'application/json'},
            }).then((res)=>{
              alert(res.data.message)
              dispatch(initStatusChange());
              navigate('/') 
            })
        } catch (error) {
            console.error(error);
        }
    }

    const ExportHandler = async ()=>{
        try {
            await axios({method: "GET", 
                url: "/api/export", 
                responseType: 'arraybuffer',
                //headers: {responseType: 'blob'},
            }) .then((res)=>{
                console.log(res)
                const blob = new Blob([res.data], { type: 'application/zip' });
                saveAs(blob, 'MarkForInstructions.zip');
            })     
        } catch (error) {
            console.error(error);
        }
    }

    return (
        <div className='flex'>
        <Nav isActive="instractionMark"></Nav>
        <main>
            <h1>Разметки инструкций</h1>

            <div>
                
            </div>

            <div className='flex jc-sb mt-3 mb-1'>
                <Button className="me-2 btn-color-active"  typeBtn="Light_btn" onClick={saveChangesHandler} disabled={drugs_changes.length === 0}>Сохранить изменения</Button>
                <div className='flex '>
                
                <Button className="me-2" typeBtn = "Light_btn"><img src={filter}/>Сортировать по</Button>
                {/* <Button className="me-2" typeBtn = "Light_btn"><img  src={plus}/>Добавить все графы</Button> */}
                <Button typeBtn="Light_btn" onClick={navigate_AddDrug}><img src={plus} />Добавить ЛС</Button>
                </div>
            </div>

            

            <Table></Table>

            <div className='flex jc-sb mt-2'>
                <StatisticGrugs></StatisticGrugs> 
                <div>
                    <Button typeBtn="Primary_btn" onClick={ExportHandler}>Экспортировать</Button>
                </div> 
                
            </div>
            
            
        </main>
        </div>
    )
}

export default MarkForInstructions
