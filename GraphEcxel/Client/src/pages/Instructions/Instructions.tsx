import Nav from '../../components/Nav/Nav'
import Button from '../../components/Button/Button'
import Searcher from '../../components/Forms/Searcher/Searcher'

import plus from "../../assets/plus.svg"
import filter from "../../assets/filter.svg"
import FilesList from '../../components/FilesList/FilesList'

function Instructions(){
    return (
        <div className='flex'>
            <Nav isActive="instructionsfiles"></Nav>
            <main >
                <h1>Инструкции к лекарственным средствам</h1>
                <div className='flex jc-sb mt-3 mb-1'>
                    <Searcher></Searcher>
                    <div className='flex '>
                        <Button className="me-2" typeBtn = "Light_btn"><img src={filter}/>Сортировать по</Button>
                        <Button typeBtn="Light_btn"><img src={plus} />Добавить инструкции</Button>
                    </div>
                </div>
                <div>
                    <FilesList>
                        
                    </FilesList>
                </div>
            </main>
        </div>
    )
}

export default Instructions