import { Routes, Route, Link } from 'react-router-dom';
import GraphsPage from "./pages/GraphsPage";
import ContrasPage from "./pages/ContrasPage";
import SynonymsPage from "./pages/SynonymsPage";
import FortranPage from "./pages/FortranPage";
import GraphVisualization from './pages/GraphVisualization';
import "./App.css";
import "./FormPages.css"


export default function App() {
  return (
    <div className='app-container'>
      <header>
        <h1>Загрузка/выгрузка данных</h1>
      </header>
      <nav>
        <ul>
          <li><Link to="/fortran">Данные для Фортрана</Link></li>
          <li><Link to="/graph">Семантические графы</Link></li>
          <li><Link to="/contraindications">Противопоказания</Link></li>
          <li><Link to="/synonyms">Синонимы</Link></li>
          <li><Link to="/graph-visualization">Визуализация графа</Link></li>
        </ul>
      </nav>
      <main>
        <Routes>
          <Route path="/fortran" element={<FortranPage />} />
          <Route path="/graph" element={<GraphsPage />} />
          <Route path="/contraindications" element={<ContrasPage />} />
          <Route path="/synonyms" element={<SynonymsPage/>} />
          <Route path="/graph-visualization" element={<GraphVisualization />} />
        </Routes>
      </main>
      <footer>
        <p>© 2025 Data Manager</p>
      </footer>
    </div>
  );
}
