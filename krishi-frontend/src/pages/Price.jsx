import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/axios";

export default function Price() {
    const [options, setOptions] = useState(null);
    const [form, setForm] = useState({
        state: "", district: "", commodity: ""
    });
    const [errors, setErrors] = useState({});
    const [result, setResult] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        api.get("/price/options")
        .then((res) => setOptions(res.data))
        .catch(() => setErrors({detail: "Could not load the form options."}));
    }, []);

    const handleChange = (e) => 
        setForm({ ...form, [e.target.name]: e.target.value });

    const handleStateChange = (e) => 
        setForm({ ...form, state: e.target.value, district: "" });

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrors({});
        setResult(null);
        setSubmitting(true);

        try {
            const res = await api.post("/price/", form);
            setResult(res.data);
        } catch (err) {
            setErrors(err.response?.data || { detail: "Could not reach the server." });
        } finally {
            setSubmitting(false);
        }
    }

    if (!options) {
        return errors.detail
            ? <div className="alert alert error">{errors.detail}</div>
            : <p>Loading...</p>
    }

    const districts = options.state[form.state] || [];

    return (
        <div className="feature-page">
            <div className="page-header fade-up">
                <Link to="/dashboard" className="breadcrumb">← Dashboard</Link>
                <h2>Crop Price Prediction</h2>
                <p>Predict mandi prices using historical data from Government of India records.</p>
            </div>

            <div className="card fade-up fade-up-d1" style={{ marginTop: "1.25rem" }}>
                <form onSubmit={handleSubmit}>
                    <div className="form-row">
                        <div className="form-group">
                            <label htmlFor="id_state" className="form-label">State</label>
                            <select name="state" id="id_state" className="form-input" required
                                    value={form.state} onChange={handleStateChange}>
                                <option value="">- Select State -</option>
                                {Object.keys(options.state).map((s) => (
                                    <option key={s} value={s}>{s}</option>
                                ))} 
                            </select>
                            {errors.state && <div className="form-error">{errors.state[0]}</div>} 
                        </div>

                        <div className="form-group">
                            <label htmlFor="id_district" className="form-label">District</label>
                            <select name="district" id="id_district" className="form-input" required
                                    value={form.district} onChange={handleChange} disabled={!form.state}>
                                <option value="">
                                    {form.state ? "- Select District -" : "- Select State First -"}
                                </option>
                                {districts.map((d) => (
                                    <option key={d} value={d}>{d}</option>
                                ))}
                            </select> 
                            {errors.district && <div className="form-error">{errors.district[0]}</div> } 
                        </div>
                    </div>

                    <div className="form-group">
                        <label htmlFor="id_commodity" className="form-label">Commodity</label>
                        <select name="commodity" id="id_commodity" className="form-input" required
                                value={form.commodity} onChange={handleChange}>
                            <option value="">- Select Commodity -</option>
                            {options.commodities.map((c) => (
                                <option key={c} value={c}>{c}</option>
                            ))}       
                        </select>
                        {errors.commodities &&  <div className="form-error">{errors.commodities[0]}</div>}
                    </div>

                    {errors.detail && <div className="alert alert-error">{errors.detail}</div>}

                    <button type="submit" className="btn-primary" disabled={submitting}>
                            {submitting ? "Predicting..." : "predict Price"}
                    </button> 
                </form>
            </div>

            {result && (
                <div className="result-card fade-up">
                    <div className="result-label">Predicted Mandi Price</div>
                    <div className="result-value">
                        ₹{result.predicted_price.toFixed(2)}{" "}
                        <span style={{ fontSize: "1rem", color: "var(--text-muted)" }}>/ quintal</span>
                    </div>
                    <div className="result-grid" style={{ marginTop: "1rem" }}>
                        <div className="result-mini">
                            <div className="rm-label">Commodity</div>
                            <div className="rm-val">{result.commodity}</div>
                        </div>
                        <div className="result-mini">
                            <div className="rm-label">State</div>
                            <div className="rm-val">{result.state}</div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}