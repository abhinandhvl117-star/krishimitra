import { useState } from "react";
import { Link } from "react-router-dom";
import  api from "../api/axios";

const EMPTY = {
    nitrogen: "", phosphorus: "", potassium: "",
    temperature: "", humidity: "", ph: "", rainfall: ""
}

const SOIL = [
    { name: "nitrogen", label: "Nitrogen(N)", placeholder: "eg. 90" },
    { name: "phosphorus", label: "Phosphorus (P)", placeholder: "eg. 80" },
    { name: "potassium", label: "Potassium (K)", placeholder: "eg. 75" },
];

const ENV = [
    { name: "temperature", label: "Temperature (C)", placeholder: "eg. 32" },
    { name: "humidity", label: "Humidity (%)", placeholder: "eg. 65" },
    { name: "ph", label: "PH Level", placeholder: "eg. 6.7" },
    { name: "rainfall", label: "Rainfall (mm)", placeholder: "eg. 100" },
];

function Field({ name, label, placeholder, value, error, onChange }) {
    return (
        <div className="form-group">
            <label htmlFor={`id_${name}`} className="form-label">{label}</label>
            <input type="number" className="form-input" step="0.1" required
                id={`id_${name}`} name={name} placeholder={placeholder}
                value={value} onChange={onChange}
            />
            {error && <div className="form-error">{error[0]}</div>} 
        </div>
    );
}

export default function Crop() {
    const [form, setForm] = useState(EMPTY);
    const [errors, setErrors] = useState({});
    const [result, setResult] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    const handleChange = (e) => 
        setForm({ ...form, [e.target.name]: e.target.value });

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrors({});
        setResult(null);
        setSubmitting(true);

        try {
            const res = await api.post("/auth/crop/", form);
            setResult(res.data);
        } catch (err) {
            setErrors(err.response?.data || { detail: "Could not react the server" });
        } finally {
            setSubmitting(false);
        }
    };

    const renderField = (f) => (
        <Field key={f.name} {...f} value={form[f.name]}
               error={errors[f.name]} onChange={handleChange} />
    );

    return (
        <div className="feature-page">
            <div className="page-header fade-up">
                <Link to="/dashboard" className="breadcrumb">Dashboard</Link>
                <h2>Crop Recommendation</h2>
                <p>Enter your soil profile and environmental data to get a personalized crop suggestion.</p>
            </div>

            <div className="card fade-up fade-up-d1">
                <form onSubmit={handleSubmit}>
                    <div className="form-section-label">Soil Nutrients (kg/ha)</div>
                    <div className="form-row-3">{SOIL.map(renderField)}</div>

                    <div className="form-section-label" style={{ marginTop: "0.5rem" }}>
                        Environmental Conditions
                    </div>
                    <div className="form-row">{ENV.map(renderField)}</div>

                    {errors.detail && <div className="alert alert-error">{errors.detail}</div>}

                    <button type="submit" className="btn-primary" disabled={submitting}>
                        {submitting ? "Analysing..." : "Get Recommendation"}
                    </button>
                </form>
            </div>

            {result && (
                <div className="result-card fade-up">
                    <div className="result-label">Recommended Crop</div>
                    <div className="result-value">{result.crop}</div>
                    <div className="result-grid" style={{ marginTop: "1rem" }}>
                        <div className="result-mini">
                            <div className="rm-label">Nitrogen (N)</div>
                            <div className="rm-val">{result.n} kg/ha</div>
                        </div>
                        <div className="result-mini">
                            <div className="rm-label">Phosphorous (P)</div>
                            <div className="rm-val">{result.p} kg/ha</div>
                        </div>
                        <div className="result-mini">
                            <div className="rm-label">Potassium (K)</div>
                            <div className="rm-val">{result.k} kg/ha</div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

