import { createContext, useContext, useState, useEffect } from "react";
import api from "../api/axios";

const AuthContext = createContext(null);

export function AuthProvider({children}) {
    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)

    // on page load: if a token exists, ask the backend who we are
    useEffect(() => {
        if (!localStorage.getItem('access')) {
            setLoading(false);
            return;
        }

        api.get("/auth/me/")
            .then((res) => setUser(res.data))
            .catch(() => {
                localStorage.removeItem('access');
                localStorage.removeItem('refresh');
            }).finally(() => setLoading(false));
    }, [])
    // login
    const login = async (username, password) => {
        const {data} = await api.post("/auth/login/", {username, password});
        localStorage.setItem('access', data.access);
        localStorage.setItem('refresh', data.refresh);

        const me = await api.get('/auth/me/');
        setUser(me.data);
        return me.data;
    }
    // logout
    const logout = () => {
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        setUser(null);
    }

    return (
        <AuthContext.Provider value={{ user, loading, login, logout }}>
            { children }
        </AuthContext.Provider>
    )
}

export const useAuth = () => useContext(AuthContext)