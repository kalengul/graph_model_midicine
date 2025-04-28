import { useEffect } from 'react';
import { BrowserRouter } from 'react-router-dom';
import {useRoutes}  from './routes';
import { useAppDispatch } from './redux/hooks';
import { Nav } from './components/nav/nav';
import {fetchDrugsList} from './redux/DrugManageSlice'

function App() {
  const routes = useRoutes()
  const dispatch = useAppDispatch()
  useEffect(()=>{
    dispatch(fetchDrugsList())
  }, [dispatch])

  return (
    <>
      
        <BrowserRouter>
          <div className="flex">
            <Nav></Nav>
            <main className="ms-2 p-3 w-100">
              {routes}
            </main>
          </div>
        </BrowserRouter>
      </>
  )
}

export default App
