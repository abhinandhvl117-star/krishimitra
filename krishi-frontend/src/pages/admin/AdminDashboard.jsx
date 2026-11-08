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
    ]
}