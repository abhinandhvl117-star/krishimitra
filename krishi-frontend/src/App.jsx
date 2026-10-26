import { Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Crop from './pages/Crop'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import ProtectedRoute from './components/ProtectedRoute'


function App() {
  return (
    <>
      <Navbar />

      <Routes>
        <Route path='/' element={ <Home /> }/>
        <Route path='/crop' element={ <Crop /> }/>
        <Route path='/login' element={ <Login/> }/>
        <Route path='/register' element={ <Register/> }/>
        <Route path='/dashboard' element={<ProtectedRoute><Dashboard /></ProtectedRoute>}/>
        
      </Routes>
    </>
  )
}

export default App
