// import {ISideEffectComputationFortran} from "../../redux/ComputationSlice"
import { ISideEffectComputation } from "../../redux/Interfaces"

export interface ICompareData{
  se_name: string,
  rankFortran: number | "-",
  rankBayes: number,
}

export interface ICompareDataRisk{
  compatibility: string,
  compareData: ICompareData[]
}

//Построение данных для сравнения
export const CreateCompareFunction = (resBayes: ISideEffectComputation[], resFortran: ISideEffectComputation[]): ICompareDataRisk[] => {
    let compareData: ICompareDataRisk[] = []

    if(!resBayes||!resFortran||resBayes.length===0||resFortran.length===0) return []
    else{
        //Заполняем ранги и побочки для Байеса
        compareData = resBayes.map(item =>({
            compatibility: item.compatibility,
            compareData: item.effects.map(se=>({
                    se_name: se.se_name,
                    rankFortran:  "-",
                    rankBayes: se.rank,
                }))
        }))
        // console.log(compareData)

        //Заполняем данные из фортрана
        resFortran.forEach(group =>
            compareData.forEach(elem=>{
                group.effects.forEach(effect=>{
                    const index= elem.compareData.findIndex(item => item.se_name.trim().toLowerCase() === effect.se_name.trim().toLowerCase());
                    if (index !== -1){
                        elem.compareData[index].rankFortran = effect.rank
                    }
                })
            })
        )

        // console.log(compareData)
        return compareData
    }

}