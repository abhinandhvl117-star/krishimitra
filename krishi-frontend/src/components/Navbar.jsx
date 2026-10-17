import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar(){
    const { user, logout } = useAuth;
    return(
        <nav>
            <div className="nav-link">
                <Link to={"/"}>Krishi</Link>
                {" | "}
                <Link to={"/crop"}>Crop</Link>
                {" | "}
                <Link to={"/login"}>Login</Link>
            </div>
        </nav>
    );
};