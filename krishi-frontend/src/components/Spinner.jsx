export default function Spinner() {
    return (
            <div style={{display: "flex", justifyContent: "center", alignItems: "center", height: "100vh"}}>
                    <div className="spinner-border" role="status" style={{color: "var(--green-600)"}}></div>
            </div>
    )
}