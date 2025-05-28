import React from 'react'; 

interface IRankCellProps{
  drugId: string; 
  seId: string;
  GetRankHandler: (drugId: string, seId: string) => string;
  rankChangeHandler: (drugId: string, seId: string, value: string) => void;
}

export const RankCell = React.memo((props: IRankCellProps) => {
  return (
    <input
      type="text"
      value={props.GetRankHandler(props.drugId, props.seId)}
      onChange={(e) => props.rankChangeHandler(props.drugId, props.seId, e.target.value)}
      className="form-control form-control-sm"
      style={{ width: '60px' }}
    />
  )
})
