import "./messageCards.scss"

interface IPropsErrMessageCard {
    message : string,
}

export const ErrMessageCard = (props: IPropsErrMessageCard) =>{
    return (
        <div className="card w-100 mc-err">
            <div className="card-body">
                <h5 className="mb-4">Ой, что-то пошло не так</h5>
                {Array.isArray(props.message.split(".")) && props.message.split(".").map((str: string)=>
                    <p className="mt-1">{str}</p>
                )}
                
            </div>
        </div>
    )
}