import { NavLink ,Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar(){
    const { user, logout } = useAuth();
    return(
        <nav>
            <Link to={"/"} className="nav-logo">
                <div className="logo-icon">
                    <svg viewBox="0 0 24 24"><path d="M17 8C8 10 5.9 16.17 3.82 21.34L5.71 22l1-2.3A4.49 4.49 0 0 0 8 20C19 20 22 3 22 3c-1 2-8 2-9 8"/></svg>
                </div>
                <span className="logo-text">Krishi<span>Mitra</span></span>
            </Link>
            <div className="nav-links">
                {user ? (
                    user.is_staff ? (
                        <>
                            <NavLink to={"/admin-panel"}>Admin</NavLink>
                            <Link to={"/"} className="nav-logout" onClick={logout}>Logout</Link>
                        </>
                    ):(
                        <>
                            <NavLink to="/" end>Home</NavLink>
                            <NavLink to="/dashboard">Dashboard</NavLink>
                            <NavLink to="/price">price</NavLink>
                            <NavLink to="/crop">Crop</NavLink>
                            <Link to="/" className="nav-logout" onClick={logout}>Logout</Link>
                        </>
                    )
                ) : (
                    <Link to="/login" className="nav-cta">Login</Link>
                )}
            </div>
        </nav>
    );
};