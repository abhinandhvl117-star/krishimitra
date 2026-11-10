import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";  
import Footer from "../components/Footer";

const FEATURES = [
  { to: "/crop",    icon: "🌾", bg: "var(--green-50)", title: "Crop Recommendation", text: "Get the best crop for your soil nutrients and local climate conditions." },
  { to: "/disease", icon: "🔬", bg: "var(--coral-50)", title: "Disease Detection",   text: "Upload a photo of your plant and get an instant AI diagnosis." },
  { to: "/price",   icon: "📈", bg: "var(--amber-50)", title: "Price Prediction",    text: "Predict mandi prices and find the best time to sell your harvest." },
  { to: "/weather", icon: "🌦️", bg: "var(--teal-50)",  title: "Weather Insights",    text: "Real-time forecasts with farming-specific advice for your region." },
  { to: "/chatbot", icon: "💬", bg: "var(--green-50)", title: "AI Chatbot",          text: "Ask any agricultural question in plain language, 24/7." },
];

const STATS = [
  { num: "94%",  label: "Disease detection accuracy" },
  { num: "500+", label: "Mandi markets tracked" },
  { num: "22",   label: "Crops supported" },
];

export default function Home() {
  const { user } = useAuth();

  return (
    <>
      <div className="hero fade-up">
        <div className="hero-badge">
          <svg width="8" height="8" viewBox="0 0 8 8" fill="currentColor"><circle cx="4" cy="4" r="4" /></svg>
          AI-Powered Agricultural Platform
        </div>
        <h1>Smart farming decisions,<br /><em>powered by AI</em></h1>
        <p>KrishiMitra brings crop intelligence, disease detection, market prices, and weather forecasts together — so every farmer can make confident, data-driven choices.</p>
        <div className="hero-actions">
          {user
            ? <Link to="/dashboard" className="btn-primary">Go to Dashboard</Link>
            : <Link to="/register" className="btn-primary">Get started free</Link>}
          <Link to="/chatbot" className="btn-secondary">Talk to KrishiMitra →</Link>
        </div>
      </div>

      <div className="features-grid fade-up fade-up-d1" style={{ margin: "3rem auto 0", maxWidth: 960 }}>
        {FEATURES.map((f) => (
          <Link key={f.to} to={f.to} className="feature-cell">
            <div className="feature-icon" style={{ background: f.bg }}>{f.icon}</div>
            <h3>{f.title}</h3>
            <p>{f.text}</p>
          </Link>
        ))}
      </div>

      <div className="stats-row fade-up fade-up-d2">
        {STATS.map((s) => (
          <div key={s.label}>
            <div className="stat-num">{s.num}</div>
            <div className="stat-label">{s.label}</div>
          </div>
        ))}
      </div>

      <Footer />
    </>
  );
}