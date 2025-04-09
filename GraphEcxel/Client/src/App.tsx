
import { BrowserRouter } from 'react-router-dom';
import {useRoutes}  from './routes';

import './App.css'

function App() {
  const routes = useRoutes()
  return (
    <>
      
        <BrowserRouter>
          {routes}
        </BrowserRouter>
      </>
  )
}

export default App
