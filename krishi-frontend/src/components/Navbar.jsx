import { Link } from "react-router-dom";

export default function Navbar(){
    return(
        <nav>
            <Link to={"/"}>Krishi</Link>
            {" | "}
            <Link to={"/crop"}>Crop</Link>
        </nav>
    );
};