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

function renderInline(test) {
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
            <div className={`msg-avatar ${isBot ? "bot" : "user-av"}`}>{isBot ? "KM" : "YOu"}</div>
            <div className="msg-bubble">{children}</div>
        </div>
    );
}

export default function Chatbot() {
    const [messages, setMessages] = useState(null);
}