import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import api from "../../api/axios";
import useFetch from "../../hooks/useFetch";
import { Loading, ScrollCard, StatusBadge, Table } from "./AdminUi";
import { cropCols, day, diseaseCols, priceCols } from "./adminColumns";

export default function AdminUserDetail() {
  const { id } = useParams();                       // the :id in /admin-panel/users/:id
  const { data, error, setData } = useFetch(`/admin/users/${id}/`);
  const [message, setMessage] = useState("");

  if (!data) return <Loading error={error} />;
  const u = data.user;

  const toggle = async () => {
    if (!window.confirm(`${u.active ? "Disable" : "Enable"} account for ${u.username}?`)) return;
    try {
      const res = await api.post(`/admin/users/${u.id}/toggle/`);
      setData((prev) => ({ ...prev, user: { ...prev.user, active: res.data.active } }));
      setMessage(`Account '${u.username}' has been ${res.data.active ? "enabled" : "disabled"}.`);
    } catch {
      setMessage("Could not update the account. Please try again.");
    }
  };

  const info = [
    ["Full Name", u.full_name || "—"],
    ["Username", `@${u.username}`],
    ["Email", u.email || "—"],
    ["City", u.city || "—"],
    ["Joined", day(u.joined)],
  ];

  return (
    <>
      {message && <div className="alert alert-success" style={{ marginBottom: "1rem" }}>{message}</div>}

      <div className="profile-header">
        <div className="profile-avatar-lg">{u.username[0].toUpperCase()}</div>
        <div style={{ flex: 1 }}>
          <div className="profile-name">{u.full_name || u.username}</div>
          <div className="profile-username">@{u.username}</div>
          <div className="profile-meta">
            Joined {day(u.joined)} &nbsp;·&nbsp;{" "}
            <span style={{ color: u.active ? "var(--green-400)" : "var(--coral-400)" }}>
              ● {u.active ? "Active" : "Disabled"}
            </span>
          </div>
        </div>
        <div className="profile-actions">
          <button type="button" onClick={toggle}
                  className={`toggle-btn ${u.active ? "toggle-disable" : "toggle-enable"}`}
                  style={{ padding: "8px 18px", fontSize: "0.825rem" }}>
            {u.active ? "Disable User" : "Enable User"}
          </button>
          <Link to="/admin-panel/users" className="btn-secondary btn-sm">← Back</Link>
        </div>
      </div>

      <div className="detail-grid">
        {info.map(([label, value]) => (
          <div className="detail-cell" key={label}>
            <div className="dc-label">{label}</div>
            <div className="dc-val">{value}</div>
          </div>
        ))}
        <div className="detail-cell">
          <div className="dc-label">Account Status</div>
          <div className="dc-val"><StatusBadge active={u.active} /></div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))", gap: "1rem", marginBottom: "1.5rem" }}>
        <div className="metric-card"><div className="label">Crop Predictions</div><div className="value">{u.crops}</div><span className="badge badge-green">Total</span></div>
        <div className="metric-card"><div className="label">Disease Scans</div><div className="value">{u.scans}</div><span className="badge badge-coral">Total</span></div>
        <div className="metric-card"><div className="label">Price Predictions</div><div className="value">{u.prices}</div><span className="badge badge-amber">Total</span></div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
        <ScrollCard title="🌾 Crop Predictions" count={`${u.crops} total`}>
          <Table rows={data.crops} empty="No predictions yet"
                 columns={[cropCols.crop, cropCols.npk, cropCols.date]} />
        </ScrollCard>
        <ScrollCard title="🔬 Disease Scans" count={`${u.scans} total`}>
          <Table rows={data.diseases} empty="No scans yet"
                 columns={[diseaseCols.disease, diseaseCols.crop, diseaseCols.date]} />
        </ScrollCard>
        <ScrollCard title="💹 Price Predictions" count={`${u.prices} total`} style={{ gridColumn: "1 / -1" }}>
          <Table rows={data.prices} empty="No predictions yet"
                 columns={[priceCols.commodity, priceCols.state, priceCols.district, priceCols.price, priceCols.date]} />
        </ScrollCard>
      </div>
    </>
  );
}
