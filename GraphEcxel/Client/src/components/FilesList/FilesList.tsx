import "./FilesList.scss"
import FileEarmarkCode from "../../assets/file-earmark-code.svg" 
import Button from "../Button/Button"

function FilesList(){
    return(
        <div className="mt-4 scroll-fileList pe-4">
            <div className="card file-card mb-3">
                <div className="card-body flex jc-sb">
                    <div>
                        <img className="icon-s me-2" alt="plusCircle" src={FileEarmarkCode}/>
                        <span>{`Амодарон.pdf`}</span>
                    </div>
                    <div>
                        <Button typeBtn="Download_icon" className="me-3"></Button>
                        <Button typeBtn="Delete_icon"></Button>
                    </div>
                   
                </div>
            </div>

            <div className="card file-card mb-3">
                <div className="card-body flex jc-sb">
                    <div>
                        <img className="icon-s me-2" alt="plusCircle" src={FileEarmarkCode}/>
                        <span>{`Противогриппозная и противопневмококковая вакцинация.pdf`}</span>
                    </div>
                    <div>
                        <Button typeBtn="Download_icon" className="me-3"></Button>
                        <Button typeBtn="Delete_icon"></Button>
                    </div>
                   
                </div>
            </div>

            <div className="card file-card mb-3">
                <div className="card-body flex jc-sb">
                    <div>
                        <img className="icon-s me-2" alt="plusCircle" src={FileEarmarkCode}/>
                        <span>{`Амодарон.pdf`}</span>
                    </div>
                    <div>
                        <Button typeBtn="Download_icon" className="me-3"></Button>
                        <Button typeBtn="Delete_icon"></Button>
                    </div>
                   
                </div>
            </div>

            <div className="card file-card mb-3">
                <div className="card-body flex jc-sb">
                    <div>
                        <img className="icon-s me-2" alt="plusCircle" src={FileEarmarkCode}/>
                        <span>{`Амодарон.pdf`}</span>
                    </div>
                    <div>
                        <Button typeBtn="Download_icon" className="me-3"></Button>
                        <Button typeBtn="Delete_icon"></Button>
                    </div>
                   
                </div>
            </div>

            <div className="card file-card mb-3">
                <div className="card-body flex jc-sb">
                    <div>
                        <img className="icon-s me-2" alt="plusCircle" src={FileEarmarkCode}/>
                        <span>{`Амодарон.pdf`}</span>
                    </div>
                    <div>
                        <Button typeBtn="Download_icon" className="me-3"></Button>
                        <Button typeBtn="Delete_icon"></Button>
                    </div>
                   
                </div>
            </div>

            <div className="card file-card mb-3">
                <div className="card-body flex jc-sb">
                    <div>
                        <img className="icon-s me-2" alt="plusCircle" src={FileEarmarkCode}/>
                        <span>{`Амодарон.pdf`}</span>
                    </div>
                    <div>
                        <Button typeBtn="Download_icon" className="me-3"></Button>
                        <Button typeBtn="Delete_icon"></Button>
                    </div>
                   
                </div>
            </div>

            <div className="card file-card mb-3">
                <div className="card-body flex jc-sb">
                    <div>
                        <img className="icon-s me-2" alt="plusCircle" src={FileEarmarkCode}/>
                        <span>{`Амодарон.pdf`}</span>
                    </div>
                    <div>
                        <Button typeBtn="Download_icon" className="me-3"></Button>
                        <Button typeBtn="Delete_icon"></Button>
                    </div>
                   
                </div>
            </div>
            
        </div>
    )
}

export default FilesList