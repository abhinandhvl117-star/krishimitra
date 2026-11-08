import { useEffect, useState } from "react";
import api from "../api/axios";

export default function useFetch(url) {
    const [data, setData] = useState(null);
    const [error, setError] = useState("");

    useEffect(() => {
        let ignore = false;
        api.get(url)
            .then((res) => {
                if (!ignore) {
                    setData(res.data);
                    setError("");
                }
            }) 
            .catch((err) => {
                if (!ignore) setError(err.response?.data?.detail || "Could not load data.")
            });
        return () => { ignore = true; };       
    }, [url]);

    return { data, error, setData };
}