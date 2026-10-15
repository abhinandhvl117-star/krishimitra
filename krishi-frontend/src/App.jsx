import { Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Crop from './pages/Crop'


function App() {
  return (
    <>
      <Navbar />

      <Routes>
        <Route path='/' element={ <Home /> }/>
        <Route path='/crop' element={ <Crop /> }/>
      </Routes>
    </>
  )
}

export default App
