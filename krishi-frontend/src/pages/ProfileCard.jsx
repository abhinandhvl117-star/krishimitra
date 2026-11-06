import { useState } from "react";
import api from "../api/axios";
import { useAuth } from "../context/AuthContext";

const FIELDS = [
    { name: "first_name", label: "First Name", "type": "text", required: false },
    { name: "last_name", label: "Last Name", type: "text", required: false },
    { name: "username", label: "Username", type: "text", required: true },
    { name: "email", label: "Email", type: "text", required: true },
];

export default function ProfileCard() {
    const { user, setUser } = useAuth();
    const [editing, setEditing] = useState(false);
    const [form, setForm] = useState({});
    const [errors, setErrors] = useState({});
    const [saving, setSaving] = useState(false);
    const [success, setSuccess] = useState("");

    const startEdit = () => {
        setForm({
            first_name: user.first_name, last_name: user.last_name,
            username: user.name, email: user.email,
        });
        setErrors({});
        setSuccess("");
        setEditing(true);
    };

    const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrors({});
        setSaving(true);

        try {
            const res = await api.patch("/auth/me/", form);
            setUser(res.data);
            setSuccess("Profile updataed successfully! ✅");
            setEditing(false);
        } catch (err) {
            setErrors(err.response?.data || { detail: "Could not reach the server." })
        } finally {
            setSaving(false);
        }
    };

    const renderField = (f) => (
        <div className="form-group" key={f.name}>
            <label htmlFor={`id_${f.name}`} className="form-label">{f.label}</label>
            <input type={f.type} className="form-input" id={`id_${f.name}`}
                    name={f.name} required={f.required} value={form[f.name] ?? ""} onChange={handleChange} />
            {errors[f.name] && <div className="form-error">{errors.name}[0]</div>} 
        </div>
    );

    return (
        <div className="card fade-up fade-up-d3" style={{ marginTop: "1rem" }}>
            <div className="card-header">
                <span className="card-title">✏️ Edit Profile</span>
                {!editing && <button type="button" className="card-action" onClick={startEdit}>Edit</button>} 
            </div>

            {success && !editing && <div className="alert alert-success" style={{ marginBottom: "1rem" }}>{success}</div>}

            {editing ? (
                <form onSubmit={handleSubmit}>
                    {errors.detail && <div className="alert alert-error">{errors.detail}</div>}
                    <div className="form-row">{FIELDS.slice(0, 2).map(renderField)}</div>
                    <div className="form-row">{FIELDS.slice(2).map(renderField)}</div>
                    <div style={{ display: "flex", gap: "8px", marginTop: "0.25rem" }}>
                        <button type="submit" className="btn-primary btn-sm" disabled={saving}>
                            {saving ? "Saving..." : "Save Changes"}
                        </button>
                        <button type="button" className="btn-secondary btn-sm" onClick={() => setEditing(false)}>
                        Cancel
                        </button>
                    </div>
                </form>
            ) : (
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(160px,1fr))",
                            gap: "1rem", padding: "0.25rem 0" }}>
                <div className="profile-info-cell"><div className="pic-label">First Name</div><div className="pic-val">{user.first_name || "—"}</div></div>
                <div className="profile-info-cell"><div className="pic-label">Last Name</div><div className="pic-val">{user.last_name || "—"}</div></div>
                <div className="profile-info-cell"><div className="pic-label">Username</div><div className="pic-val">@{user.username}</div></div>
                <div className="profile-info-cell"><div className="pic-label">Email</div><div className="pic-val">{user.email || "—"}</div></div>
                </div>
            )}
        </div>
    );
}