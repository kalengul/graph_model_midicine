import { useEffect } from 'react';
import { BrowserRouter } from 'react-router-dom';
import {useRoutes}  from './routes';
import { useAppDispatch } from './redux/hooks';
import {fetchDrugsList} from './redux/DrugManageSlice'
import { fetchContraindicationssList } from './redux/ContraindicationsManageSlice';
import { initStates } from './redux/ComputationSlice';
import { checkAuth } from './redux/AuthSlice';

import { Nav } from './components/nav/nav';

function App() {
  const routes = useRoutes()
  const dispatch = useAppDispatch()
  useEffect(()=>{
    Promise.all([
      dispatch(fetchDrugsList()),
      dispatch(fetchContraindicationssList()),
      dispatch(initStates())
    ])
  }, [dispatch])

  useEffect(()=>{
    dispatch(checkAuth());
  }, [dispatch])
  

  return (
    <>
    
      
      <BrowserRouter>
        <div className="flex">
          <Nav></Nav>
          {routes}
        </div>
      </BrowserRouter>
      
    </>
)
}

export default App
