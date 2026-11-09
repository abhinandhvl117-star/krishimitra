import useFetch from "../../hooks/useFetch";
import { Loading, ScrollCard, Table } from "./AdminUi";
import { cropCols, diseaseCols, priceCols } from "./adminColumns";

// one component behind all three "all records" pages
function AdminList({ url, title, columns, empty }) {
  const { data, error } = useFetch(url); 
  if (!data) return <Loading error={error} />;

  const count = data.total > data.results.length
    ? `latest ${data.results.length} of ${data.total}`
    : `${data.total} total`;

  return (
    <ScrollCard title={title} count={count} maxHeight="calc(100vh - 220px)">
      <Table columns={columns} rows={data.results} empty={empty} />
    </ScrollCard>
  );
}

export function AdminCrops() {
  return (
    <AdminList url="/admin/crops/" title="🌾 All Crop Predictions" empty="No crop predictions yet"
      columns={[cropCols.user, cropCols.crop, cropCols.n, cropCols.p, cropCols.k, cropCols.temp,
                cropCols.humidity, cropCols.ph, cropCols.rainfall, cropCols.date]} />
  );
}

export function AdminDiseases() {
  return (
    <AdminList url="/admin/diseases/" title="🔬 All Disease Scans" empty="No disease scans yet"
      columns={[diseaseCols.user, diseaseCols.disease, diseaseCols.crop, diseaseCols.part, diseaseCols.date]} />
  );
}

export function AdminPrices() {
  return (
    <AdminList url="/admin/prices/" title="💹 All Price Predictions" empty="No price predictions yet"
      columns={[priceCols.user, priceCols.commodity, priceCols.state, priceCols.district, priceCols.price, priceCols.date]} />
  );
}
