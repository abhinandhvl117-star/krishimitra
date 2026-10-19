import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext"

export default function Login() {
    const { login } = useAuth();
    const navigate = useNavigate();
    const [identifier, setIdentifier] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [submitting, setSubmitting] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("")
        setSubmitting(true)

        try {
            const user = await login(identifier, password);
            navigate(user.is_staff ? "/admin-panel" : "/dashboard")
        } catch (err) {
            const data = err.response?.data;
            setError(data?.detail || data?.non_field_errors?.[0] || "Login failed. please try again.")
        } finally {
            setSubmitting(false)
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-card fade-up">
                <h2>Welcome back</h2>
                <p className="auth-sub">Login to access your KrishiMitra dashboard.</p>

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="id_username" className="form-label">Username</label>
                        <input type="text" className="form-input" id="id_username"
                        value={identifier} onChange={(e) => setIdentifier(e.target.value)}
                        autoComplete="username" required/>
                    </div>

                    <div className="form-group">
                        <label htmlFor="id_password" className="form-label">password</label>
                        <input type="password" className="form-input" id="id_password"
                        value={password} onChange={(e) => {setPassword(e.target.value)}}
                        autoComplete="current-password" required/>
                    </div>

                    {error && <div className="alert alert-error" style={{ marginBottom: "1rem" }}>{error}</div>}

                    <div style={{ textAlign: "right", marginBottom: "1rem" }}>
                        <Link to="/forgot-password"
                        style={{ fontSize: "0.8rem", color: "var(--green-400)", textDecoration: "none" }}>
                            Forgot password?
                        </Link>
                    </div>
                    <button className="btn-primary" type="submit"
                    style={{ width: "100%", justifyContent: "center" }} disabled={submitting}>
                        {submitting? "Logging in.." : "Login"}
                    </button>
                </form>
                
                <hr className="divider" />
                <div className="auth-footer">
                    Don't have an account? <Link to="/register">Register here</Link>
                </div>
            </div>
        </div>
    )
};