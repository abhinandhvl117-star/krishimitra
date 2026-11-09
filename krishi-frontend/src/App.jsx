import { Routes, Route } from "react-router-dom";
import MainLayout from "./components/MainLayout";
import AdminLayout from "./pages/admin/AdminLayout";
import Home from './pages/Home'
import Crop from './pages/Crop'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Price from './pages/Price'
import Disease from './pages/Disease'
import Weather from './pages/Weather'
import Chatbot from './pages/Chatbot'
import ProtectedRoute from './components/ProtectedRoute'
import AdminDashboard from "./pages/admin/AdminDashboard";
import AdminUsers from "./pages/admin/AdminUsers";
import AdminUserDetail from "./pages/admin/AdminUserDetail";
import { AdminCrops, AdminDiseases, AdminPrices } from "./pages/admin/AdminList";


function App() {
  return (
    <>
      <Routes>
          {/* farmer site: uses the green main navbar */}
          <Route element={<MainLayout />}>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/crop" element={<ProtectedRoute><Crop /></ProtectedRoute>} />
            <Route path="/price" element={<ProtectedRoute><Price /></ProtectedRoute>} />
            <Route path="/disease" element={<ProtectedRoute><Disease /></ProtectedRoute>} />
            <Route path="/weather" element={<ProtectedRoute><Weather /></ProtectedRoute>} />
            <Route path="/chatbot" element={<ProtectedRoute><Chatbot /></ProtectedRoute>} />
          </Route>

          {/* admin site: uses its own dark navbar (inside AdminLayout) */}
          <Route path="/admin-panel"
              element={<ProtectedRoute adminOnly><AdminLayout /></ProtectedRoute>}>
            <Route index element={<AdminDashboard />} />
            <Route path="users" element={<AdminUsers />} />
            <Route path="users/:id" element={<AdminUserDetail />} />
            <Route path="crops" element={<AdminCrops />} />
            <Route path="diseases" element={<AdminDiseases />} />
            <Route path="prices" element={<AdminPrices />} />
          </Route>
        </Routes>
    </>
  )
}

export default App
