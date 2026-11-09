import { Link, NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import "../../styles/admin.css";

const icon = (children) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">{children}</svg>
);

const LINKS = [
  { to: "/admin-panel", label: "Dashboard", end: true,
    icon: icon(<><rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" /><rect x="14" y="14" width="7" height="7" /><rect x="3" y="14" width="7" height="7" /></>) },
  { sep: true },
  { to: "/admin-panel/users", label: "Users",
    icon: icon(<><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M23 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" /></>) },
  { to: "/admin-panel/crops", label: "Crops",
    icon: icon(<path d="M17 8C8 10 5.9 16.17 3.82 21.34L5.71 22l1-2.3A4.49 4.49 0 0 0 8 20C19 20 22 3 22 3c-1 2-8 2-9 8" />) },
  { to: "/admin-panel/diseases", label: "Diseases",
    icon: icon(<><circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" /></>) },
  { to: "/admin-panel/prices", label: "Prices",
    icon: icon(<><line x1="12" y1="1" x2="12" y2="23" /><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" /></>) },
];

export default function AdminLayout() {
  const { user, logout } = useAuth();
  const name = [user.first_name, user.last_name].filter(Boolean).join(" ") || user.username;

  return (
    <>
      <nav className="admin-topnav">
        <Link className="topnav-logo" to="/admin-panel">
          <div className="logo-icon">
            <svg viewBox="0 0 24 24"><path d="M17 8C8 10 5.9 16.17 3.82 21.34L5.71 22l1-2.3A4.49 4.49 0 0 0 8 20C19 20 22 3 22 3c-1 2-8 2-9 8" /></svg>
          </div>
          <span className="logo-text">Krishi<span>Mitra</span></span>
          <span className="admin-badge">Admin</span>
        </Link>

        <div className="topnav-links">
          {LINKS.map((l, i) =>
            l.sep ? (
              <div className="topnav-sep" key={i} />
            ) : (
              <NavLink key={l.to} to={l.to} end={l.end}
                       className={({ isActive }) => `topnav-link ${isActive ? "active" : ""}`}>
                {l.icon}
                <span>{l.label}</span>
              </NavLink>
            )
          )}
        </div>

        <div className="topnav-right">
          <div className="topnav-user">
            <div className="topnav-avatar">{user.username[0].toUpperCase()}</div>
            <span className="topnav-username">{name}</span>
          </div>
          <Link to="/" className="topnav-logout" onClick={logout}>
            {icon(<><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" /></>)}
            Logout
          </Link>
        </div>
      </nav>

      <main className="admin-content">
        <Outlet />   {/* the matching child route renders here */}
      </main>
    </>
  );
}
