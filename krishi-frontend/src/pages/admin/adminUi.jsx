import { Link } from "react-router-dom";

export function Loading({ error }) {
    return error ? <div className="alert alert-error">{error}</div> : <p>Loading...</p>
}

export function ScrollCard({ title, count, link, maxHeight, style, children }) {
    return (
        <div className="scroll-card" style={style}>
            <div className="scroll-card-header">
                <span className="scroll-card-title">{title}</span>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    {count != null && <span className="scroll-card-count">{count}</span>}
                    {link && (
                        <Link to={link} style={{ fontSize: "0.75rem", color: "var(--green-400)", textDecoration: "none" }}>
                            View all →
                        </Link>
                    )} 
                </div>
            </div>
            <div className="scroll-card-body" style={maxHeight ? { maxHeight } : undefined}>
                {children}
            </div>
        </div>
    );
}

export function Table({ columns, rows, empty, rowClass }) {
    return (
        <table className="admin-table">
            <thead>
                <tr>{columns.map((c, i) => <th key={i}>{c.header}</th>)}</tr>
            </thead>
            <tbody>
                {rows.length === 0 && (
                    <tr>
                        <td colSpan={columns.length}
                            style={{ textAlign: "center", color: "var(--text-muted)", padding: "2rem" }}>
                            {empty}
                        </td>
                    </tr>
                )}
                {rows.map((row) => (
                    <tr key={row.id} className={rowClass ? rowClass(row) : undefined}>
                        {columns.map((c, i) => <td key={i}>{c.render(row)}</td>)} 
                    </tr>
                ))}
            </tbody>
        </table>
    );
}

export function statusBadge({ active }) {
    return active
        ? <span className="badge badge-green">Active</span>
        : <span className="badge badge-coral">Disable</span>;
}

export function viewLink({ to }) {
    return (
        <Link to={to} className="icon-btn" title="view user">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                <circle cx="12" cy="12" r="3" />
            </svg>
        </Link>
    );
}