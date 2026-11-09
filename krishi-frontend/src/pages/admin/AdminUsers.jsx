import { useEffect, useState } from "react";
import api from "../../api/axios";
import useFetch from "../../hooks/useFetch";
import { Loading, ScrollCard, StatusBadge, Table, ViewLink } from "./AdminUi";
import { day } from "./adminColumns";

const SORTS = [
  ["date_desc", "Newest"],
  ["date_asc", "Oldest"],
  ["alpha_asc", "A → Z"],
  ["alpha_desc", "Z → A"],
];

export default function AdminUsers() {
  const [sort, setSort] = useState("date_desc");
  const [search, setSearch] = useState("");     // what the admin has typed
  const [q, setQ] = useState("");               // debounced copy that actually triggers a request
  const [message, setMessage] = useState({ type: "", text: "" });

  // wait 300ms after the last keystroke before searching
  useEffect(() => {
    const t = setTimeout(() => setQ(search.trim()), 300);
    return () => clearTimeout(t);
  }, [search]);

  const { data, error, setData } = useFetch(`/admin/users/?sort=${sort}&q=${encodeURIComponent(q)}`);

  const toggle = async (u) => {
    if (!window.confirm(`${u.active ? "Disable" : "Enable"} ${u.username}?`)) return;
    try {
      const res = await api.post(`/admin/users/${u.id}/toggle/`);
      // update just that row in place, no refetch needed
      setData((prev) => ({
        ...prev,
        results: prev.results.map((r) => (r.id === u.id ? { ...r, active: res.data.active } : r)),
      }));
      setMessage({ type: "success", text: `Account '${u.username}' has been ${res.data.active ? "enabled" : "disabled"}.` });
    } catch {
      setMessage({ type: "error", text: "Could not update the account. Please try again." });
    }
  };

  if (!data) return <Loading error={error} />;

  const columns = [
    {
      header: "User",
      render: (u) => (
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div style={{ width: 32, height: 32, borderRadius: "50%", background: "var(--green-400)", color: "white",
                        display: "flex", alignItems: "center", justifyContent: "center",
                        fontSize: "0.75rem", fontWeight: 600, flexShrink: 0 }}>
            {u.username[0].toUpperCase()}
          </div>
          <div>
            <div style={{ fontWeight: 500, fontSize: "0.825rem" }}>{u.full_name || u.username}</div>
            <div style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>@{u.username}</div>
          </div>
        </div>
      ),
    },
    { header: "Email", render: (u) => <span style={{ color: "var(--text-muted)", fontSize: "0.78rem" }}>{u.email || "—"}</span> },
    { header: "City", render: (u) => <span style={{ fontSize: "0.78rem" }}>{u.city || "—"}</span> },
    { header: "Joined", render: (u) => <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>{day(u.joined)}</span> },
    {
      header: "Predictions",
      render: (u) => (
        <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
          🌾 {u.crops} &nbsp; 🔬 {u.scans} &nbsp; 💹 {u.prices}
        </span>
      ),
    },
    { header: "Status", render: (u) => <StatusBadge active={u.active} /> },
    {
      header: "Action",
      render: (u) => (
        <button type="button" onClick={() => toggle(u)}
                className={`toggle-btn ${u.active ? "toggle-disable" : "toggle-enable"}`}>
          {u.active ? "Disable" : "Enable"}
        </button>
      ),
    },
    { header: "", render: (u) => <ViewLink to={`/admin-panel/users/${u.id}`} /> },
  ];

  return (
    <>
      {message.text && (
        <div className={`alert alert-${message.type === "success" ? "success" : "error"}`} style={{ marginBottom: "1rem" }}>
          {message.text}
        </div>
      )}

      <div className="scroll-card">
        <div className="scroll-card-header" style={{ gap: "0.75rem" }}>
          <span className="scroll-card-title">
            👥 All Users <span className="scroll-card-count" style={{ marginLeft: 6 }}>{data.total} total</span>
          </span>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
            {SORTS.map(([key, label]) => (
              <button key={key} type="button" onClick={() => setSort(key)}
                      className={`sort-btn ${sort === key ? "sort-active" : ""}`}
                      style={{ cursor: "pointer", fontFamily: "inherit" }}>
                {label}
              </button>
            ))}
          </div>
        </div>

        <div style={{ padding: "0.75rem 1.25rem", borderBottom: "0.5px solid var(--border)", background: "var(--gray-50)" }}>
          <div className="search-wrap" style={{ maxWidth: 400 }}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input className="search-input" type="text" autoComplete="off" autoFocus
                   placeholder="Search by name, username or email…"
                   value={search} onChange={(e) => setSearch(e.target.value)} />
          </div>
        </div>

        <div className="scroll-card-body" style={{ maxHeight: "calc(100vh - 280px)" }}>
          <Table columns={columns} rows={data.results}
                 empty={q ? "No users match your search." : "No users registered yet"}
                 rowClass={(u) => (u.active ? "" : "row-disabled")} />
        </div>
      </div>
    </>
  );
}
