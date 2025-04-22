import {useAppDispatch, useAppSelector} from '../../redux/hooks';
import {updateRank} from "../../redux/SideEffectManageSlice"
import "./sideEffectsTable.scss"

import { debounce } from 'lodash';
import {useMemo} from "react"

export const SideEffectsTable = ()=>{
    const dispatch = useAppDispatch()

    const drugs = useAppSelector((state)=>state.drugManage.drugs)
    const sideEffects = useAppSelector((state)=>state.sideEffectManage.sideEffects)
    const ranks = useAppSelector((state)=>state.sideEffectManage.ranks)

    const GetRankHandler = (drug_id: string, se_id: string) =>{
        const rank = ranks.find(rank=>rank.drug_id===drug_id && rank.se_id ===se_id)
        return  rank ? rank.rank : 0
    }

    const rankChangeHandler =  useMemo(() => debounce(
        (drug_id: string, se_id: string, newRank: string) => {
          dispatch(updateRank({drug_id, se_id, value: newRank}));
        },
        300 // Задержка 300мс
    ), [dispatch])

    return (
    <div className='SE-table scroll'>
        <table className="table table-hover table-bordered sticky-header-table">
            <thead>
                <tr>
                    <th scope="col" className="sticky-col-1">#</th>
                    <th scope="col" className="sticky-col-2">ПЭ/ЛС</th>
                    {Array.isArray(drugs) && drugs.map((drug) =>
                        <th scope="col" key={drug.id}>{drug.drug_name}</th>
                    )}
                </tr>
            </thead>
            <tbody>
                {Array.isArray(sideEffects) && sideEffects.map((sideEffect, index) =>
                    <tr key={sideEffect.id}>
                        <th className="sticky-col-1">{index + 1}</th>
                        <th className="sticky-col-2">{sideEffect.se_name}</th>
                        {Array.isArray(drugs) && drugs.map((drug) =>
                            <td key={`${drug.id} ${sideEffect.id}`} >
                                <input
                                    type="text"
                                    value={GetRankHandler(drug.id, sideEffect.id)}
                                    onChange={(e) => rankChangeHandler(drug.id, sideEffect.id, e.target.value)}
                                    className="form-control form-control-sm"
                                    style={{ width: '60px' }}
                                />
                            </td>
                        )}
                    </tr>
                )}
            </tbody>
        </table>
    </div>
    )
}