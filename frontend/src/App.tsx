import { BrowserRouter } from 'react-router-dom';
import {useRoutes}  from './routes';

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
