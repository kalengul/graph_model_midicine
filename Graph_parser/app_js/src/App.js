import logo from './logo.svg';
import './App.css';
import {Graph} from "./GraphComponent/Graph"
import {RiskDiagram} from "./RiskDiagramComponent/RiskDiagram"

function App() {
  return (
    <div className="App">
      {/* <h1>Диаграмма рисков</h1> */}
      {/* <RiskDiagram></RiskDiagram> */}

      <h1>Граф</h1>
      <Graph></Graph>
    </div>
  );
}

export default App;
