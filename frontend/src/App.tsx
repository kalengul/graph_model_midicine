import { useEffect } from 'react';
import { BrowserRouter } from 'react-router-dom';
import {useRoutes}  from './routes';
import { useAppDispatch } from './redux/hooks';
import {fetchDrugsList} from './redux/DrugManageSlice'
import { initStates } from './redux/ComputationSlice';
import { checkAuth } from './redux/AuthSlice';

function App() {
  const routes = useRoutes()
  const dispatch = useAppDispatch()
  useEffect(()=>{
    Promise.all([
      dispatch(fetchDrugsList()),
      dispatch(initStates())
    ])
  }, [dispatch])

  useEffect(()=>{
    dispatch(checkAuth());
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
