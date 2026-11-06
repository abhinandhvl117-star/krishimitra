import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/axios";
import { useAuth } from "../context/AuthContext";
import ProfileCard from "./ProfileCard";

function greeting() {
  const h = new Date().getHours();              
  if (h < 12) return "Good morning";
  if (h < 17) return "Good afternoon";
  return "Good evening";
}

const shortDate = (iso) =>
  new Date(iso).toLocaleDateString("en-IN", { day: "2-digit", month: "short" });
const longDate = (iso) =>
  new Date(iso).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "numeric", minute: "2-digit" });

const ACTIVITY_STYLE = {
  crop:    { color: "var(--green-400)", badge: "green", tag: "Crop" },
  disease: { color: "var(--coral-400)", badge: "coral", tag: "Disease" },
  price:   { color: "var(--amber-400)", badge: "amber", tag: "Price" },
};

const QUICK_ACTIONS = [
  { to: "/crop", icon: "🌾", title: "Get Crop Advice", desc: "Enter soil data to get a recommendation" },
  { to: "/disease", icon: "📷", title: "Scan Plant", desc: "Upload a photo for disease detection" },
  { to: "/price", icon: "💹", title: "Check Prices", desc: "View mandi rates and predictions" },
  { to: "/chatbot", icon: "💬", title: "Ask KrishiMitra", desc: "Get instant farming guidance" },
];

export default function Dashboard() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/dashboard/")
      .then((res) => setData(res.data))
      .catch(() => setError("Could not load your dashboard. Please refresh."));
  }, []);

  if (error) return <div className="alert alert-error">{error}</div>;
  if (!data) return <p>Loading...</p>;

  const { weather, latest_crop, latest_price, latest_disease, activity } = data;
  const fullName = [user.first_name, user.last_name].filter(Boolean).join(" ");

  return (
    <div className="dashboard">
      <div className="dash-header fade-up"
           style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start",
                    flexWrap: "wrap", gap: "1rem", marginBottom: "2rem" }}>
        <div>
          <h2>{greeting()} 🌿</h2>
          <p>Here's what's happening on your farm today</p>
        </div>
        <div className="user-profile-card">
          <div className="user-profile-avatar">{user.username[0].toUpperCase()}</div>
          <div className="user-profile-info">
            <div className="user-profile-name">{fullName || user.username}</div>
            <div className="user-profile-username">@{user.username}</div>
            {user.email && <div className="user-profile-email">{user.email}</div>}
          </div>
        </div>
      </div>

      <div className="metric-cards fade-up fade-up-d1">
        <div className="metric-card">
          <div className="label">Recommended Crop</div>
          <div className="value" style={{ fontSize: "1.2rem", fontWeight: 500 }}>{latest_crop?.name ?? "—"}</div>
          <div className="sub">Based on your last soil input</div>
          <span className="badge badge-green">
            {latest_crop ? `Last: ${shortDate(latest_crop.date)}` : "Run analysis"}
          </span>
        </div>

        <div className="metric-card">
          <div className="label">Today's Temperature</div>
          <div className="value">{weather?.temp ?? "—"}<span style={{ fontSize: "1rem" }}>°C</span></div>
          <div className="sub">{weather?.description ?? "Weather unavailable"}</div>
          <span className="badge badge-amber">Humidity {weather?.humidity ?? "—"}%</span>
        </div>

        <div className="metric-card">
          <div className="label">{latest_price?.commodity ?? "Commodity"} Price</div>
          <div className="value" style={{ fontSize: "1.3rem", fontWeight: 500 }}>
            ₹{latest_price?.price != null ? Math.round(latest_price.price) : "—"}
          </div>
          <div className="sub">per quintal · {latest_price?.district ?? "your district"}</div>
          <span className="badge badge-teal">{latest_price ? `Last: ${shortDate(latest_price.date)}` : "Check prices"}</span>
        </div>

        <div className="metric-card">
          <div className="label">Plant Health</div>
          <div className="value" style={{ fontSize: "1.2rem", fontWeight: 500 }}>{latest_disease?.name ?? "—"}</div>
          <div className="sub">{latest_disease ? `Last scan: ${shortDate(latest_disease.date)}` : "No scan yet"}</div>
          <span className="badge badge-green">{latest_disease ? "Scanned" : "Scan a plant"}</span>
        </div>
      </div>

      <div className="dash-grid fade-up fade-up-d2">
        <div className="card">
          <div className="card-header"><span className="card-title">Recent Activity</span></div>
          <div className="activity-list">
            {activity.length === 0 && (
              <p style={{ fontSize: "0.825rem", color: "var(--text-muted)", textAlign: "center", padding: "1.5rem 0" }}>
                No activity yet — try a crop recommendation or disease scan!
              </p>
            )}
            {activity.map((a) => {
              const s = ACTIVITY_STYLE[a.type];
              return (
                <div className="activity-item" key={`${a.type}-${a.created_at}`}>
                  <div className="activity-dot" style={{ background: s.color }} />
                  <div className="activity-info">
                    <div className="title">{a.title}</div>
                    <div className="time">{longDate(a.created_at)} · {a.detail}</div>
                  </div>
                  <span className={`activity-tag badge badge-${s.badge}`}>{s.tag}</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Current Weather</span>
            <Link to="/weather" className="card-action">Details →</Link>
          </div>
          <div className="weather-card">
            <div className="weather-main">
              <div className="weather-temp">{weather?.temp ?? "—"}°</div>
              <div className="weather-info">
                <div className="location">{weather?.city ?? "Set location in Weather page"}</div>
                <div className="desc">
                  {weather?.description}{weather && ` · Feels like ${weather.feels_like}°`}
                </div>
              </div>
            </div>
            <div className="weather-stats">
              <div className="weather-stat"><div className="wlabel">Humidity</div><div className="wval">{weather?.humidity ?? "—"}%</div></div>
              <div className="weather-stat"><div className="wlabel">Rainfall</div><div className="wval">{weather?.rainfall ?? "—"} mm</div></div>
              <div className="weather-stat"><div className="wlabel">Wind</div><div className="wval">{weather?.wind ?? "—"} km/h</div></div>
              <div className="weather-stat"><div className="wlabel">Feels like</div><div className="wval">{weather?.feels_like ?? "—"}°</div></div>
            </div>
            {!weather && (
              <div style={{ textAlign: "center", padding: "1rem 0" }}>
                <Link to="/weather" className="btn-primary btn-sm">Set your location →</Link>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="card fade-up fade-up-d3">
        <div className="card-header"><span className="card-title">Quick Actions</span></div>
        <div className="quick-actions">
          {QUICK_ACTIONS.map((q) => (
            <Link key={q.to} to={q.to} className="qa-btn">
              <span className="qa-icon">{q.icon}</span>
              <span className="qa-title">{q.title}</span>
              <span className="qa-desc">{q.desc}</span>
            </Link>
          ))}
        </div>
      </div>

      <ProfileCard />
    </div>
  );
}