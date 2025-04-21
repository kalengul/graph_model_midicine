export interface IComputationMedScapeData{
    se_name?: string
}

interface IErrors{
    se_name?: string,
}


export const ComputationMedScapeValidator = (values: IComputationMedScapeData)=>{
    const errors: IErrors = {}

    return errors
}