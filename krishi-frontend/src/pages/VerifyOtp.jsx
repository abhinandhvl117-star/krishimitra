import { useEffect, useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import api from "../api/axios";

const COOLDOWN = 60; 

export default function VerifyOtp() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const email = state?.email;

  const [otp, setOtp] = useState("");
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [loading, setLoading] = useState(false);
  const [seconds, setSeconds] = useState(COOLDOWN);

  useEffect(() => {
    if (seconds <= 0) return;
    const t = setTimeout(() => setSeconds((s) => s - 1), 1000);
    return () => clearTimeout(t);
  }, [seconds]);

  if (!email) return <Navigate to="/forgot-password" replace />;

  async function handleSubmit(e) {
    e.preventDefault();
    setError(""); setInfo("");
    setLoading(true);
    try {
      const { data } = await api.post("/auth/verify-otp/", { email, otp });
      navigate("/reset-password", { state: { uid: data.uid, token: data.token }, replace: true });
    } catch (err) {
      const d = err.response?.data;
      setError(d?.otp?.[0] || d?.detail || "Something went wrong. Try again.");
    } finally {
      setLoading(false);
    }
  }

  async function resend() {
    setError(""); setInfo("");
    try {
      await api.post("/auth/forgot-password/", { email });
      setInfo("A new code has been sent.");
      setOtp("");
      setSeconds(COOLDOWN);
    } catch {
      setError("Could not resend. Try again.");
    }
  }

  return (
    <div className="auth-card">
      <h2>🔐 Enter your code</h2>
      <p>We sent a 6-digit code to <strong>{email}</strong>. It expires in 5 minutes.</p>
      {error && <div className="alert alert-error">{error}</div>}
      {info && <div className="alert alert-success">{info}</div>}
      <form onSubmit={handleSubmit}>
        <input
          className="otp-input" type="text" inputMode="numeric" autoComplete="one-time-code"
          maxLength={6} placeholder="······" autoFocus required
          value={otp}
          onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))}  // digits only
        />
        <button className="btn btn-primary" disabled={loading || otp.length !== 6}>
          {loading ? "Verifying..." : "Verify"}
        </button>
      </form>
      <p className="auth-footer">
        Didn't receive it?{" "}
        {seconds > 0
          ? <span>Resend in {seconds}s</span>
          : <button type="button" className="link-btn" onClick={resend}>Resend OTP</button>}
      </p>
      <p className="auth-footer"><Link to="/login">Back to Login</Link></p>
    </div>
  );
}
