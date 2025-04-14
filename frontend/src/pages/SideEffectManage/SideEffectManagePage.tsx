import { Nav } from "../../components/nav/nav"
import "./SideEffectManage.scss"
export const SideEffectManage = () =>{
    return(
        <div className="flex">
            <Nav></Nav>
            <main className="ms-2 p-3 w-100">
                <h1>Управление побочными эффектами</h1>
            </main>
        </div>
    )
}