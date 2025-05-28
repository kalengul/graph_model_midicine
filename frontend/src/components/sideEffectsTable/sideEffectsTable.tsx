import {useAppDispatch, useAppSelector} from '../../redux/hooks';
import {updateRank} from "../../redux/SideEffectManageSlice"
import "./sideEffectsTable.scss"

import { debounce } from 'lodash';
import {useMemo, useCallback} from "react"

 import { RankCell } from './rankCell';

export const SideEffectsTable = ()=>{
    const dispatch = useAppDispatch()

    const drugs = useAppSelector((state)=>state.drugManage.drugs)
    const sideEffects = useAppSelector((state)=>state.sideEffectManage.sideEffects)
    const ranks = useAppSelector((state)=>state.sideEffectManage.ranks)

    const ranksMap = useMemo(() => {
        const map = new Map<string, string>();
        if(Array.isArray(ranks)){
            ranks.forEach(rank => {
                map.set(`${rank.drug_id}-${rank.se_id}`, rank.rank);
            });
        } 
        return map;
      }, [ranks]);

    const GetRankHandler = useCallback((drug_id: string, se_id: string) => {
        return ranksMap.get(`${drug_id}-${se_id}`) || '0';
    }, [ranksMap]);

    const rankChangeHandler =  useMemo(() => debounce(
        (drug_id: string, se_id: string, newRank: string) => {
          dispatch(updateRank({drug_id, se_id, value: newRank}));
        },
        100 // Задержка 100мс
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
                            <td key={`${drug.id}-${sideEffect.id}`} >
                                <RankCell drugId={drug.id} seId={sideEffect.id} GetRankHandler={GetRankHandler} rankChangeHandler={rankChangeHandler}/>
                            </td>
                        )}
                    </tr>
                )}
            </tbody>
        </table>
    </div>
    )
}