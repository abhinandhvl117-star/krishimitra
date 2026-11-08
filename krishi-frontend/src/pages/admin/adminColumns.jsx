import { statusBadge, viewLink } from "./AdminUi";

export const dt = (iso) => 
    new Date(iso).toLocaleDateString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit", hour12: false });
export const day = (iso) =>
    new Date(iso).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });

const muted = { fontSize: "0.75rem", color: "var(--text-muted)" };
const small = { fontSize: "0.78rem" };

const text = (header, key, style = {}) => ({
    header,
    render: (r) => <span style={{ ...small, ...style }}>{r[key]}</span>
})

const username = { header: "User", render: (r) => <span style={{ fontWeight: 500, fontSize: "0.8rem" }}>{r.username}</span> }; 
const date = { header: "Date", render: (r) => <span style={muted}>{dt(r.created_at)}</span> };

export const cropCols = {
  user: username,
  date,
  crop: { header: "Crop", render: (r) => <span className="badge badge-green" style={{ textTransform: "capitalize" }}>{r.crop}</span> },
  npk: { header: "N · P · K", render: (r) => <span style={muted}>{r.nitrogen} · {r.phosphorus} · {r.potassium}</span> },
  n: text("N", "nitrogen"),
  p: text("P", "phosphorus"),
  k: text("K", "potassium"),
  temp: { header: "Temp", render: (r) => <span style={small}>{r.temperature}°C</span> },
  humidity: { header: "Humidity", render: (r) => <span style={small}>{r.humidity}%</span> },
  ph: text("pH", "ph"),
  rainfall: { header: "Rainfall", render: (r) => <span style={small}>{r.rainfall}mm</span> },
};

export const diseaseCols = {
  user: username,
  date,
  disease: { header: "Detected Disease", render: (r) => <span className="badge badge-coral" style={{ whiteSpace: "normal", lineHeight: 1.4 }}>{r.disease_name}</span> },
  crop: text("Crop", "crop_type", { textTransform: "capitalize" }),
  part: text("Part", "affected_part", { textTransform: "capitalize" }),
};

export const priceCols = {
  user: username,
  date,
  commodity: { header: "Commodity", render: (r) => <span className="badge badge-amber">{r.commodity}</span> },
  state: text("State", "state"),
  district: text("District", "district"),
  price: { header: "Predicted Price", render: (r) => <span style={{ fontWeight: 500 }}>{r.price != null ? `₹${r.price.toFixed(2)}` : "—"}</span> },
};

export const userCols = {
  person: {
    header: "User",
    render: (u) => (
      <>
        <div style={{ fontWeight: 500 }}>{u.full_name || u.username}</div>
        <div style={muted}>@{u.username}</div>
      </>
    ),
  },
  city: { header: "City", render: (u) => <span style={small}>{u.city || "—"}</span> },
  joined: { header: "Joined", render: (u) => <span style={muted}>{day(u.joined)}</span> },
  status: { header: "Status", render: (u) => <StatusBadge active={u.active} /> },
  view: { header: "", render: (u) => <ViewLink to={`/admin-panel/users/${u.id}`} /> },
};
