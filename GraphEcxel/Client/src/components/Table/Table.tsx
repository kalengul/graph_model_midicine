import {useState, useEffect} from 'react'
import {useNavigate} from 'react-router-dom'
import axios from 'axios'

import { useDispatch , useSelector} from 'react-redux';
import {addValue, addIsAllSelected, addIsSelectedRows,addChandedGrapg, deleteIsSelectedRows, deleteDrug, initSelected} from '../../redux/DrugsSlice'

import './table.scss'
import Select from '../Forms/Select/Select'
import Button from '../Button/Button'
import Modal from '../Modals/Modal';
import DropdownMenu from '../DropdownMenu/DropdownMenu'

function Table() {
    const navigate = useNavigate();

    const dispatch = useDispatch()
    const [graphStates, setGraphStates] = useState([])

    useEffect(() => {
        dispatch(initSelected())
        try {
            axios({ 
                method: "GET", 
                url: "/api/getstates", 
            }).then((res)=>{
                setGraphStates(res.data) //Доваление в useState
            }).then(()=>axios({ 
                method: "GET", 
                url: "/api/getall", 
            })).then((res)=>{
              //Сохранение данных для отображения
              dispatch(addValue(res.data));
            })
        } catch (err) {console.error(err)}
    }, [])

    const drugs = useSelector(state=>state.drugs.drugs)
    const isAllSelected = useSelector(state=>state.drugs.isAllSelected)
    const isSelectedRows = useSelector(state=>state.drugs.isSelectedRows)

    const selectAllHandler = (event) =>{
        dispatch(addIsAllSelected(event.target.checked))

        if(event.target.checked){//Если выбрано все
            drugs.forEach(drug => {
                dispatch(addIsSelectedRows(drug.id))
            });
        }else dispatch(initSelected())
    }

    const selectRowHandler = (event)=>{
        if(event.target.checked) dispatch(addIsSelectedRows(event.target.id))
        else dispatch(deleteIsSelectedRows(event.target.id))
    }



    const [modalShow, setModalShow] = useState(false);
    const [selectedDrug, setSelectedDrug] = useState(null);

    const handleOpen = (drug) => {
        setSelectedDrug(drug);   // сохраняем выбранный элемент
        setModalShow(true);      // открываем модальное окно
    };

    const handleClose = () => {
        setModalShow(false);
        setSelectedDrug(null);
    };


    const deleteHandler = async(event) =>{
        const id = selectedDrug.id

        try {
            const response = await axios({ 
                method: "DELETE", 
                url: `/api/deletedrug/${id}`, 
            }).then((res)=>{
                //обновление отображения
                dispatch(deleteDrug(selectedDrug.id))
                
                setModalShow(false);
                setSelectedDrug(null);

            })
        } catch (e) {}

    }

    const updateHandler = (event, drug) =>{ 
        dispatch(addChandedGrapg(drug.id))
        navigate(`/drugs/${drug.id}`) 
    }


    return (
        <div className='scroll mb-2'>
            <table className="table table-sm table-hover table-striped sticky-header-table">
            <thead>
                <tr>
                    <th scope="col"><input className="form-check-input" type="checkbox" value="all" checked={isAllSelected} onChange={selectAllHandler}/></th>
                    <th scope="col">Лекарственное средство</th>
                    <th scope="col">Состояние графа</th>
                    <th scope="col">Отображение графа</th>
                    <th scope="col"></th>
                </tr>
            </thead>
            <tbody className='align-items-center table-success scroll-tbody'>
                {Array.isArray(drugs) && drugs.map((drug, index)=>
                    <tr key={drug.id}>
                        <th scope="row"><input id={drug.id} className="form-check-input" type="checkbox" value="all" checked={isSelectedRows.includes(drug.id)} onChange={selectRowHandler}/></th>
                        <td>{drug.drug_name.charAt(0).toUpperCase() + drug.drug_name.slice(1).toLowerCase()}</td>
                        <td><Select type="tableSelect" id ={drug.id} options = {graphStates} activeOption = {drug.status}></Select></td>
                        <td>{drug.graph_name && drug.graph_name != null && 
                            <a className="link-opacity-75" href="#">{drug.graph_name}</a>}
                        </td>
                        <td>
                            <div className="btn-group">
                                <Button className="dropdown-toggle" typeBtn="Three-dots_icon" dataBsToggle="dropdown" ariaExpanded="false"/>

                                <ul className="dropdown-menu">
                                    <li><a className="dropdown-item" href="#" onClick = {()=>updateHandler(event, drug)}>Изменить</a></li>

                                    <li><hr className="dropdown-divider" /></li>

                                    {(drug.graph_name!=null) && 
                                        <>
                                            <li><a className="dropdown-item" href="#">Экспортировать в .json</a></li>
                                            <li><a className="dropdown-item" href="#">Экспортировать в .html</a></li>

                                            <li><hr className="dropdown-divider" /></li>
                                        </>
                                    }
                                    
                                    <li><a className="dropdown-item" href="#" onClick={() => handleOpen(drug)}>Удалить</a></li>
                                </ul>
                            </div>
                        </td>
                    </tr>

                )}
            </tbody>
            </table>

            <Modal show={modalShow} handleClose={handleClose} title="Подтверждение удаления" onConfirm={deleteHandler}>
                {selectedDrug && (
                <>
                    Вы действительно хотите удалить лекарственное средство {selectedDrug.drug_name}?
                </>)}
            </Modal>
        </div>
    )
  }
  
  export default Table