import { useState } from "react";
import { Link } from "react-router-dom"
import api from "../api/axios"

const MAX_MB = 10;

export default function Disease() {
    const [file, setFile] = useState(null);
    const [error, setError] = useState("")
    const [result, SetResult] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    const handleFile = (e) => {
        const picked = e.target.files[0];
        SetResult(null);
        setError("");
        if (picked && picked.size > MAX_MB * 1024 * 1024) {
            setError(`Image must be under ${MAX_MB} MB.`);
            e.target.value = "";
            setFile(null);
            return;
        }
        setFile(picked || null)
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file) return;
        setError("");
        SetResult(null);
        setSubmitting(true);
        try {
            const formData = new FormData();
            formData.append("image", file);
            const res = await api.post("/disease", formData);
            SetResult(res.data);
        } catch (err) {
            const data = err.response?.data;
            setError(data?.detail || data?.image?.[0] || "Could not reach the server.");
        } finally {
            setSubmitting(false)
        }
    };

    return (
        <div className="feature-page">
            <div className="page-header fade-up">
                <Link to="/dashboard" className="breadcrumb">← Dashboard</Link>
                <h2>Plant Disease Detection</h2>
                <p>Upload a clear photo of the affected plant leaf or stem for AI diagnosis</p>
            </div>

            <form onSubmit={handleSubmit}>
                <div className="upload-zone fade-up fade-up-d1">
                    <input type="file" id="disease-image" accept="image/*" onChange={handleFile} />
                    <span className="upload-icon">📷</span>
                    {file ? (
                        <p><strong>{file.name}</strong> selected - ready to analyze</p>
                    ) : (
                        <p><strong>Click to upload</strong> or drag and drop your plant photo here</p>
                    )} 
                    <p style={{ marginTop: "8px", fontSize: "0.78rem"}}>Support JPG, PNG, WEBP · Max {MAX_MB} MB</p>
                </div>

                {error && <div className="alert alert-error">{error}</div>} 

                <button type="submit" className="btn-primary" disabled={!file || submitting}>
                    {submitting ? "Analysing..." : "Analyze Image"}
                </button>
            </form>

            {result && (
                <div className="result-card fade-up">
                    <div className="disease-result">
                        <div className="disease-badge"
                            style={{ background: result.healthy ? "var(--green-50)" : "var(--coral-50)" }}>
                            {result.healthy ? "🌿" : "🍂" }
                        </div>
                        <div className="disease-info">
                            <h3>{result.disease_name}</h3>
                            <div className="confidence">Detected on: {result.crop} · leaf</div>
                        </div>
                    </div>
                    <div className="treatment-list">
                        {result.cause && (
                            <div style={{ marginBottom: "1rem" }}>
                                <div className="tlabel">Cause</div>
                                <div className="treatment-item">{result.cause}</div>
                            </div>
                        )}
                        {result.cure && (
                            <div>
                                <div className="tlabel">Recommended Treatment</div>
                                <div className="treatment-item">{result.cure}</div>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}