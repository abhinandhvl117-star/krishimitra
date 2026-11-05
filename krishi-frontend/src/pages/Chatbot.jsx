import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/axios"

const CHIPS = [
    { icon: "🌾", label: "Kharif crop advice", text: "What crop should I plant this Kharif season in Kerala?" },
    { icon: "🔬", label: "Leaf disease help", text: "My tomato leaves have brown spots with yellow rings. What disease is it?" },
    { icon: "💰", label: "MSP rates", text: "What is the current MSP for rice in 2025-26?" },
    { icon: "🏛️", label: "Govt schemes", text: "How do I apply for PM-KISAN scheme?" },
    { icon: "💧", label: "Irrigation timing", text: "When should I irrigate paddy during tillering stage?" },
    { icon: "🧪", label: "Fertilizer advice", text: "What fertilizer should I use for sandy soil with low nitrogen?" },
];

function renderInline(text) {
    return text.split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
        part.startsWith("**") && part.endsWith("**") && part.length > 4 
        ? <strong key={i}>{part.slice(2, -2)}</strong>
        : part
    );
}

function RichText({ text }) {
    const blocks = [];
    let items = [];
    const flush = () => {
        if (items.length) {
            blocks.push(<ul key={`ul-${blocks.length}`}>{items}</ul>);
            items = []
        }
    };
    text.split("\n").forEach((line, i) => {
        const bullet = line.match(/^\s*[-•*]\s+(.*)/);
        if (bullet) {
            items.push(<li key={i}>{renderInline(bullet[1])}</li>);
        } else {
            flush();
            if (line.trim()) blocks.push(<p key={i}>{renderInline(line)}</p>);
        }
    });
    flush();
    return <>{blocks}</>;
}

function Message({role, children}) {
    const isBot = role === "bot";
    return (
        <div className={`msg ${role}`}>
            <div className={`msg-avatar ${isBot ? "bot" : "user-av"}`}>{isBot ? "KM" : "You"}</div>
            <div className="msg-bubble">{children}</div>
        </div>
    );
}

export default function Chatbot() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [sending, setSending] = useState(false);
    const [loading, setLoading] = useState(true);
    const listRef = useRef(null);
    const counter = useRef(0);

    useEffect(() => {
        api.get("/chat/")
            .then((res) => setMessages(res.data))
            .catch(() => {})
            .finally(() => setLoading(false));
    }, []);

    useEffect(() => {
        const el = listRef.current;
        if (el) el.scrollTop = el.scrollHeight;
    }, [messages,sending]);

    const addMessage = (role, content) =>
        setMessages((prev) => [...prev, { id: `local-${counter.current++}`, role, content }]);

    const send = async (text) => {
        const msg = text.trim();
        if (!msg || sending) return;
        setInput("");
        addMessage("user", msg);
        setSending(true);

        try {
            const res = await api.post("/chat/", { message: msg });
            addMessage("bot", res.data.reply);
        } catch (err) {
            const d = err.response?.data;
            addMessage("bot", d?.detail || d?.message?.[0] || "Connection error. Please try again.");
        } finally {
            setSending(false);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        send(input);
    };

    return (
        <div className="feature-page">
            <div className="page-header fade-up">
                <Link to="/dashboard" className="breadcrumb">← Dashboard</Link>
                <h2>KrishiMitra Assistand</h2>
                <p>Powered by Llama 3 · Ask anything about crops, diseases, prices, or farming advice.</p>
            </div>

            <div className="chat-container fade-up fade-up-d1">
                <div style={{ padding: "10px 1.25rem", borderBottom: "0.5px solid var(--border)",
                      display: "flex", alignItems: "center", gap: "8px" }}>
                    <span style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--green-400)",
                         display: "inline-block", animation: "pulse 2s infinite" }} />
                    <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Llama 3 · Groq</span>
                </div>

                <div className="chat-messages" ref={listRef}>
                    <Message role="bot">
                        Namaskaram! 🙏 I'm KrishiMitra, your AI farming assistant powered by Llama 3.
                        I can help you with crop selection, disease identification, mandi prices, irrigation advice,
                        government schemes, and much more. What would you like to know today?                        
                    </Message>

                    {loading && <Message role="bot">Loading your conversation...</Message>}

                    {messages.map((m) => (
                        <Message key={m.id} role={m.role}>
                            {m.role == "bot" ? <RichText text={m.content} /> : m.content}
                        </Message>
                    ))}
                </div> 

                {!loading && messages.length === 0 && !sending && (
                    <div className="chat-suggestions">
                        {CHIPS.map((c) => (
                            <button key={c.label} type="button" className="Chat-chip" onClick={() => send(c.text)}>
                                {c.icon} {c.label}
                            </button>
                        ))}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="chat-input-row">
                    <input type="text" className="chat-input" autoComplete="off" maxLength={1000}
                            placeholder="Ask KrishiMitra anything about farming..."
                            value={input} onChange={(e) => setInput(e.target.value)} disabled={sending}/>
                    <button type="submit" className={`chat-send ${sending ? "loading" : ""}`} disabled={sending}>
                        <svg viewBox="0 0 24 24" width="16" height="16">
                        <polyline points="22 2 11 13" stroke="white" strokeWidth="2" fill="none" strokeLinecap="round" />
                        <polygon points="22 2 15 22 11 13 2 9 22 2" stroke="white" strokeWidth="2" fill="none" strokeLinejoin="round" />
                        </svg>                        
                    </button>
                </form>
            </div>
        </div>
    );
}