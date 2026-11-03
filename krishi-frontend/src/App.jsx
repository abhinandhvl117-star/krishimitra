import { Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Crop from './pages/Crop'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Price from './pages/Price'
import Disease from './pages/Disease'
import ProtectedRoute from './components/ProtectedRoute'


function App() {
  return (
    <>
      <Navbar />

      <Routes>
        <Route path='/' element={ <Home /> }/>
        <Route path='/login' element={ <Login/> }/>
        <Route path='/register' element={ <Register/> }/>
        <Route path='/dashboard' element={<ProtectedRoute><Dashboard /></ProtectedRoute>}/>
        <Route path='/crop' element={<ProtectedRoute><Crop /></ProtectedRoute>} />
        <Route path='/price' element={<ProtectedRoute><Price /></ProtectedRoute>} />
        <Route path='/disease' element={<ProtectedRoute><Disease /></ProtectedRoute>} />
        
      </Routes>
    </>
  )
}

export default App
