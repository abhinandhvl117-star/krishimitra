import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/axios";

export default function Weather() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [city, setCity] = useState("");
    const [cityError, setCityError] = useState("")
    const [success, setSuccess] = useState("");
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        api.get("/weather/")
            .then((res) => setData(res.data))
            .catch((err) => setError(err.response?.data?.detail || "Could not load weather."))
            .finally(() => setLoading(false));
    }, []);

    const handleCityUpdate = async (e) => {
        e.preventDefault();
        setCityError("");
        setSuccess("");
        setSaving(true);

        try {
            const res = await api.post("/weather/", {city});
            setData(res.data);
            setError("");
            setSuccess(`Location updated to ${res.data.city}.`);
            setCity("");
        } catch (err) {
            const d = err.response?.data;
            setCityError(d?.city?.[0] || d?.detail || "Could not update location.");
        } finally {
            setSaving(false);
        }
    };

    if (loading) return <p>Loading weather...</p>;

    const w = data?.weather;

      return (
        <div className="feature-page">
        <div className="page-header fade-up">
            <Link to="/dashboard" className="breadcrumb">← Dashboard</Link>
            <h2>Weather Insights</h2>
            {data && (
            <p>Real-time weather for <strong>{data.city}</strong> with farming recommendations.</p>
            )}
        </div>

        {w ? (
            <div className="card fade-up fade-up-d1">
            <div className="weather-big">
                <div className="city">📍 {w.city}</div>
                <div className="temp-display">{w.temp}<sup>°C</sup></div>
                <div className="condition">
                {w.description} · Feels like {w.feels_like}°C · Humidity {w.humidity}%
                </div>
            </div>

            <div className="weather-detail-grid">
                <div className="wd-cell"><div className="wd-icon">🌧️</div><div className="wd-val">{w.rainfall} mm</div><div className="wd-label">Rainfall</div></div>
                <div className="wd-cell"><div className="wd-icon">💧</div><div className="wd-val">{w.humidity}%</div><div className="wd-label">Humidity</div></div>
                <div className="wd-cell"><div className="wd-icon">🌬️</div><div className="wd-val">{w.wind} km/h</div><div className="wd-label">Wind ({w.wind_dir})</div></div>
                <div className="wd-cell"><div className="wd-icon">🌡️</div><div className="wd-val">{w.temp_min}°C</div><div className="wd-label">Min Temp</div></div>
                <div className="wd-cell"><div className="wd-icon">🌡️</div><div className="wd-val">{w.temp_max}°C</div><div className="wd-label">Max Temp</div></div>
                <div className="wd-cell"><div className="wd-icon">🔆</div><div className="wd-val">{w.sunrise}</div><div className="wd-label">Sunrise</div></div>
            </div>

            {data.forecast.length > 0 && (
                <>
                <div className="form-section-label" style={{ margin: "1.5rem 0 0.75rem" }}>Forecast</div>
                <div className="forecast-row">
                    {data.forecast.map((day, i) => (
                    <div key={day.day + i} className={`forecast-day ${i === 0 ? "today" : ""}`}>
                        <div className="fd-day">{i === 0 ? "Today" : day.day}</div>
                        <div className="fd-icon">{day.icon}</div>
                        <div className="fd-hi">{day.max}°</div>
                        <div className="fd-lo">{day.min}°</div>
                    </div>
                    ))}
                </div>
                </>
            )}

            {data.advisory.length > 0 && (
                <div className="farming-advisory">
                <div className="adv-label">🌾 Farming Advisory</div>
                {data.advisory.map((tip) => <p key={tip}>{tip}</p>)}
                </div>
            )}
            </div>
        ) : (
            <div className="card fade-up" style={{ textAlign: "center", padding: "2.5rem" }}>
            <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>🌧️</div>
            <p style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>{error}</p>
            </div>
        )}

        <div className="card fade-up" style={{ marginTop: "1.25rem" }}>
            <div className="card-header">
            <span className="card-title">📍 Update Your Location</span>
            </div>
            {data && (
            <p style={{ fontSize: "0.825rem", color: "var(--text-muted)", marginBottom: "1rem" }}>
                Currently set to <strong>{data.city}</strong>. Change it to get weather for a different city.
            </p>
            )}
            <form onSubmit={handleCityUpdate}
                style={{ display: "flex", gap: "10px", alignItems: "flex-end" }}>
            <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
                <label htmlFor="id_city" className="form-label">New City / District</label>
                <input id="id_city" className="form-input" type="text" name="city" required
                    placeholder="e.g. Palakkad, Mumbai, Bengaluru" autoComplete="off"
                    value={city} onChange={(e) => setCity(e.target.value)} />
            </div>
            <button type="submit" className="btn-primary"
                    style={{ whiteSpace: "nowrap" }} disabled={saving}>
                {saving ? "Updating..." : "Update →"}
            </button>
            </form>
            {cityError && <div className="alert alert-error" style={{ marginTop: "0.75rem" }}>{cityError}</div>}
            {success && <div className="alert alert-success" style={{ marginTop: "0.75rem" }}>{success}</div>}
        </div>
    </div>
  );
}