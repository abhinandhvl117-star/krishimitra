import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Footer() {
  const { user, logout } = useAuth();

  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <div className="footer-logo">
            <div className="logo-icon" style={{ width: 28, height: 28 }}>
              <svg viewBox="0 0 24 24" style={{ width: 16, height: 16, fill: "none", stroke: "white", strokeWidth: 2, strokeLinecap: "round" }}>
                <path d="M17 8C8 10 5.9 16.17 3.82 21.34L5.71 22l1-2.3A4.49 4.49 0 0 0 8 20C19 20 22 3 22 3c-1 2-8 2-9 8" />
              </svg>
            </div>
            <span className="logo-text">Krishi<span>Mitra</span></span>
          </div>
          <p className="footer-tagline">Intelligent farming decisions powered by AI — built for every Indian farmer.</p>
          <div className="footer-contact">✉️ abhinandhvl117@gmail.com</div>
        </div>

        <div className="footer-links-group">
          <div className="footer-col">
            <div className="footer-col-title">Features</div>
            <Link to="/crop">Crop Recommendation</Link>
            <Link to="/disease">Disease Detection</Link>
            <Link to="/price">Price Prediction</Link>
            <Link to="/weather">Weather Insights</Link>
            <Link to="/chatbot">AI Chatbot</Link>
          </div>
          <div className="footer-col">
            <div className="footer-col-title">Account</div>
            {user ? (
              <>
                <Link to="/dashboard">Dashboard</Link>
                <a href="/" onClick={(e) => { e.preventDefault(); logout(); }}>Logout</a>
              </>
            ) : (
              <>
                <Link to="/register">Register</Link>
                <Link to="/login">Login</Link>
                <Link to="/forgot-password">Forgot Password</Link>
              </>
            )}
          </div>
          <div className="footer-col">
            <div className="footer-col-title">Technology</div>
            <span>React · Django · FastAPI</span>
            <span>TensorFlow · Scikit-learn</span>
            <span>Llama 3 via Groq</span>
            <span>OpenWeatherMap API</span>
            <span>Govt. of India Data</span>
          </div>
        </div>
      </div>

      <div className="footer-bottom">
        <span>© 2026 KrishiMitra AI · Built by Abhinandh Vijayan L</span>
        <span>Made with 🌿 for Indian farmers</span>
      </div>
    </footer>
  );
}