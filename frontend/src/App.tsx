import { useEffect } from 'react';
import { BrowserRouter } from 'react-router-dom';
import {useRoutes}  from './routes';
import { useAppDispatch } from './redux/hooks';
//import {fetchDrugsList} from './redux/DrugManageSlice'

function App() {
  const routes = useRoutes()
  
  const dispatch = useAppDispatch()
  useEffect(()=>{
    //dispatch(fetchDrugsList())
  }, [dispatch])

  return (
    <>
      
        <BrowserRouter>
          {routes}
        </BrowserRouter>
      </>
  )
}

export default App
