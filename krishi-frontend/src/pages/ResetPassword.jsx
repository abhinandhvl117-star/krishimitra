import { useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import api from "../api/axios";

export default function ResetPassword() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const [form, setForm] = useState({ new_password1: "", new_password2: "" });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  if (!state?.uid || !state?.token) return <Navigate to="/forgot-password" replace />;

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  async function handleSubmit(e) {
    e.preventDefault();
    setErrors({});
    setLoading(true);
    try {
      await api.post("/auth/reset-password/", { uid: state.uid, token: state.token, ...form });
      navigate("/login", {
        replace: true,
        state: { message: "Password reset successful! Please log in." },
      });
    } catch (err) {
      const d = err.response?.data || {};
      setErrors({
        new_password1: d.new_password1?.join(" "),
        new_password2: d.new_password2?.[0] ?? d.new_password2,
        general: d.detail || (!err.response && "Network error. Try again."),
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-card">
      <h2>Set a new password</h2>
      {errors.general && <div className="alert alert-error">{errors.general}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="p1">New password</label>
          <input id="p1" type="password" name="new_password1" autoComplete="new-password" required
            value={form.new_password1} onChange={handleChange} />
          {errors.new_password1 && <small className="field-error">{errors.new_password1}</small>}
        </div>
        <div className="form-group">
          <label htmlFor="p2">Confirm password</label>
          <input id="p2" type="password" name="new_password2" autoComplete="new-password" required
            value={form.new_password2} onChange={handleChange} />
          {errors.new_password2 && <small className="field-error">{errors.new_password2}</small>}
        </div>
        <button className="btn btn-primary" disabled={loading}>
          {loading ? "Saving..." : "Reset Password →"}
        </button>
      </form>
    </div>
  );
}
