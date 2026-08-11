import "./completeStatus.scss";

interface ICompleteStatus{
    status: "running" | "completed" | "canceled" | "failed";
}

const TranslateStatus = (status: string): string =>{
    if(status == "running") return "В процессе"
    if(status == "completed") return "Завершен"
    if(status == "canceled") return "Отменен"
    return "Ошибка"
}

export const CompleteStatus = (props: ICompleteStatus)=>{
    return(
        <div className={props.status}>
            {TranslateStatus(props.status)}
        </div>
    )
}