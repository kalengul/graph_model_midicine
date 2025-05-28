// import {useMemo, useCallback} from "react"

// export const RankCell = React.memo(({ drugId, seId }: { drugId: string; seId: string }) => {
//   const dispatch = useAppDispatch();
//   const rank = useAppSelector(state => {
//     const found = state.sideEffectManage.ranks.find(r => 
//       r.drug_id === drugId && r.se_id === seId
//     );
//     return found?.rank || '0';
//   });

//   const handleChange = useCallback(
//     debounce((value: string) => {
//       dispatch(updateRank({ drug_id: drugId, se_id: seId, value }));
//     }, 100),
//     [drugId, seId]
//   );

//   return (
//     <input
//       type="text"
//       defaultValue={rank}
//       onChange={(e) => handleChange(e.target.value)}
//       className="form-control form-control-sm"
//       style={{ width: '60px' }}
//     />
//   );
// });
