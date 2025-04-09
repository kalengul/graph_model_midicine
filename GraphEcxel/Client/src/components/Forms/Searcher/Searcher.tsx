import Button from "../../Button/Button"

import "./Searcher.scss"

function Searcher(props) {
    return(
        <>
         <div className="searcher-container">
            <form className="d-flex search-form">
            <input className="form-control me-2 search-input" type="search" placeholder="Поиск" aria-label="Поиск"/>
            <Button typeBtn="Light_btn" className="search-btn color-ff">Найти</Button>
            </form>
        </div>
        </>
    )
}

export default Searcher