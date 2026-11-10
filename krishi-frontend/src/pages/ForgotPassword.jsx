import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/axios";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.post("/auth/forgot-password/", { email });
      // hand the email to the next page through router state (not the URL)
      navigate("/verify-otp", { state: { email } });
    } catch (err) {
      const data = err.response?.data;
      setError(data?.email?.[0] || data?.detail || "Something went wrong. Try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-card">
      <h2>Forgot password?</h2>
      <p>Enter your email and we'll send you a 6-digit code.</p>
      {error && <div className="alert alert-error">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input id="email" type="email" name="email" autoComplete="email" required
            value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <button className="btn btn-primary" disabled={loading}>
          {loading ? "Sending..." : "Send code"}
        </button>
      </form>
      <p className="auth-footer">Remembered it? <Link to="/login">Back to Login</Link></p>
    </div>
  );
}