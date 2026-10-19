import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../api/axios"

export default function Register() {
    const navigate = useNavigate();
    const [form, setForm] = useState({
        first_name: "", last_name: "", username: "", email: "",
        city: "", password1: "", password2: "",
    });
    const [errors, setErrors] = useState({});
    const [submitting, setSubmitting] = useState(false);

    const handleChange = (e) =>
        setForm({ ...form, [e.target.name]: e.target.value})

    const handleSubmint = async (e) => {
        e.preventDefault();
        setErrors({});
        setSubmitting(true);
        try {
            await api.post("/auth/register", form);
            navigate ("/login");
        } catch (err) {
            setErrors(err.response?.data || {non_field_errors: ["Registration failded."] });
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-card fade-up">
                <h2>Create account</h2>
                <p className="auth-sub">Join KrishiMitra and start making smarter farming decisions.</p>

                <form onSubmit={handleSubmint}>
                    <div className="form-row">
                        <div className="form-group">
                            <label htmlFor="id_first_name" className="form-label">First Name</label>
                            <input type="text" name="first_name" id="id_first_name" className="form-input"
                            value={form.first_name} onChange={handleChange}
                            autoComplete="given-name" required/>
                        </div>
                        <div className="form-group">
                            <label htmlFor="id_last_name" className="form-label">Last Nmae</label>
                            <input type="text" name="last_name" id="id_last_name" className="form-input" 
                            value={form.last_name} onChange={handleChange}
                            autoComplete="family-name" required/>
                        </div>
                        <div className="form-group">
                            <label htmlFor="id_username" className="form-label">Username</label>
                            <input type="text" name="username" id="id_username" className="form-input" 
                            value={form.username} onChange={handleChange}
                            autoComplete="username" required/>

                            {errors.username && (<div className="form-error">{errors.username[0]}</div>)} 
                        </div>
                        <div className="form-group">
                            <label htmlFor="id_city" className="form-label">Your City / District</label>
                            <input type="text" name="city" id="id_city" className="form-input" 
                            value={form.city} onChange={handleChange}
                            placeholder="e.g. Kerala, Mumbai, Bengaluru" required/>

                            {errors.city && (<div className="form-error">{errors.city[0]}</div>)}
                        </div>

                        <div className="form-group">
                            <label htmlFor="id_email" className="form-label">Email</label>
                            <input type="text" name="email" id="id_email" className="form-input" 
                            value={form.email} onChange={handleChange} required/>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    )
}