import useFetch from "../../hooks/useFetch";
import { Loading, ScrollCard, Table } from "./AdminUi";
import { cropCols, diseaseCols, priceCols, userCols } from "./adminColumns";

export default function AdminDashboard() {
    const { data, error } = useFetch("/admin/overview/");
    if (!data) return <Loading error={error}/>;

    const { totals } = data;
    const cards = [
        { label: "Total Users", value: totals.users, sub: "Registered farmers", badge: "green", tag: "Active platform" },
        { label: "Crop Predictions", value: totals.crops, sub: "All time", badge: "green", tag: "Crop" },
        { label: "Disease Scans", value: totals.diseases, sub: "All time", badge: "coral", tags: "Disease" },
        { label: "Price Predictions", value: "totals.prices", sub: "All time", badge: "ambar", tag: "Price" }
    ];

    return (
        <>
        <div className="metric-cards" style={{ marginBottom: "1.5rem" }}>
            {cards.map((c) => (
                <div className="metric-card" key={c.label}>
                    <div className="label">{c.label}</div>
                    <div className="value">{c.value}</div>
                    <div className="sub">{c.sub}</div>
                    <span className={`badge badge-${c.badge}`}>{c.tag}</span>
                </div>
            ))}
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
            <ScrollCard title="👥 Recent Users" count={`${totals.users} total`} link="/admin-panel/users">
            <Table rows={data.recent_users} empty="No users yet"
                    columns={[userCols.person, userCols.city, userCols.joined, userCols.status, userCols.view]}
                    rowClass={(u) => (u.active ? "" : "row-disabled")} />
            </ScrollCard>

            <ScrollCard title="🌾 Top Recommendations" count="Last 10" link="/admin-panel/crops">
            <Table rows={data.recent_crops} empty="No predictions yet"
                    columns={[cropCols.crop, cropCols.user, cropCols.npk, cropCols.date]} />
            </ScrollCard>

            <ScrollCard title="🔬 Top Diseases" count="Last 10" link="/admin-panel/diseases">
            <Table rows={data.recent_diseases} empty="No scans yet"
                    columns={[diseaseCols.disease, diseaseCols.user, diseaseCols.crop, diseaseCols.date]} />
            </ScrollCard>

            <ScrollCard title="💹 Top Price Predictions" count="Last 10" link="/admin-panel/prices">
            <Table rows={data.recent_prices} empty="No predictions yet"
                    columns={[priceCols.commodity, priceCols.user, priceCols.district, priceCols.price, priceCols.date]} />
            </ScrollCard>
        </div>
        </>
    );
}