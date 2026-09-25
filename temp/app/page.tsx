"use client"

import { useState } from "react"
import useSWR from "swr"
import { Activity, Archive, ArrowDownToLine, ChevronRight, CircleHelp, Clock3, Code2, Command, Database, Download, Eye, FileKey2, FolderKanban, Gauge, HardDriveDownload, LayoutDashboard, LockKeyhole, MoreHorizontal, Package, PanelLeftClose, Plus, Search, Settings2, ShieldCheck, Sparkles, Terminal, UserRound, Wrench, X } from "lucide-react"

const logo = "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-Z8cHQXyHKJoczhOeP6MtROpOitbg9S.png"
const cover = "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/Copilot_20260925_002703-dfcOK0pShuZQJYCMOISR2E3s3ALR2F.png"
const API_URL = process.env.NEXT_PUBLIC_ZS_DUMPER_API_URL || "http://127.0.0.1:3011"
const fetcher = (url: string) => fetch(url, { cache: "no-store" }).then(async (response) => {
  if (!response.ok) throw new Error(`API ${response.status}`)
  return response.json().catch(() => ({ ok: true }))
})
const targets = [
  { name: "new area", host: "204.10.193.13:30120", letter: "N", status: "Ready", time: "12 min ago" },
  { name: "t-life", host: "185.200.246.197:30168", letter: "T", status: "Ready", time: "28 min ago" },
  { name: "fm", host: "185.229.237.3:30120", letter: "F", status: "Token found", time: "1 hr ago" },
  { name: "pixelar", host: "play.pixelar.fr", letter: "P", status: "Ready", time: "2 hr ago" },
]
const nav = [{ label: "Overview", icon: LayoutDashboard }, { label: "Dumper", icon: ArrowDownToLine }, { label: "Decrypt", icon: LockKeyhole }, { label: "Fixer", icon: Wrench }, { label: "Resources", icon: Package }]

export default function Home() {
  const [active, setActive] = useState("Dumper")
  const [query, setQuery] = useState("")
  const [showModal, setShowModal] = useState(false)
  const [toast, setToast] = useState("")
  const { error: apiError, isLoading: apiLoading } = useSWR(`${API_URL}/health`, fetcher, { refreshInterval: 15000, revalidateOnFocus: true })
  const apiConnected = !apiLoading && !apiError
  const filtered = targets.filter((t) => t.name.includes(query.toLowerCase()) || t.host.includes(query.toLowerCase()))
  const notify = (message: string) => { setToast(message); setTimeout(() => setToast(""), 2600) }
  return <main className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark"><img src={logo} alt="ZS Dumper logo" /></div><div><strong>ZS DUMPER</strong><span>CONTROL CENTER</span></div><button className="icon-button"><PanelLeftClose size={17} /></button></div>
      <div className="workspace"><span className="eyebrow">WORKSPACE</span><div className="workspace-row"><div className="workspace-icon"><ShieldCheck size={17} /></div><div><b>ZS-DUMPER</b><small>Windows executable</small></div><ChevronRight size={15} /></div></div>
      <nav><span className="eyebrow">NAVIGATION</span>{nav.map(({ label, icon: Icon }) => <button key={label} onClick={() => setActive(label)} className={`nav-item ${active === label ? "active" : ""}`}><Icon size={18} /><span>{label}</span>{label === "Dumper" && <span className="nav-badge">4</span>}</button>)}</nav>
      <div className="sidebar-bottom"><button className="nav-item"><Gauge size={18} /><span>Activity</span></button><button className="nav-item"><Settings2 size={18} /><span>Settings</span></button><div className="profile"><div className="avatar">M</div><div><b>mathe</b><small>Pro account</small></div><MoreHorizontal size={17} /></div></div>
    </aside>
    <section className="content">
      <header className="topbar"><div className="breadcrumbs"><Command size={15} /><span>/</span><b>{active}</b><span className="live-pill"><i /> Session active</span></div><div className="top-actions"><button className="icon-button"><CircleHelp size={18} /></button><button className="icon-button"><Activity size={18} /></button><div className="top-avatar">M</div></div></header>
      <div className="content-inner">
        <div className="hero"><div><div className="kicker"><Sparkles size={14} /> RESOURCE RECOVERY</div><h1>Server dumper</h1><p>Connecte l&apos;API locale ZS-DUMPER pour gérer tes serveurs et lancer les opérations depuis l&apos;exécutable Windows.</p><span className="api-endpoint"><Terminal size={13} /> API locale · port 3011</span></div><div className="hero-art"><img src={cover} alt="Abstract golden cyberpunk artwork" /><div className="art-overlay" /></div><div className="hero-actions"><span className={`status-chip ${apiConnected ? "connected" : "disconnected"}`}><i /> {apiLoading ? "Connecting to API..." : apiConnected ? "API connected" : "API offline"}</span><button className="outline-button" onClick={() => notify("Latest version already installed")}>v2.0.2 <ArrowDownToLine size={14} /></button></div></div>
        <div className="stats"><div className="stat-card"><div className="stat-icon purple"><FolderKanban size={18} /></div><div><span>Saved targets</span><strong>16</strong></div><small>+3 this week</small></div><div className="stat-card"><div className="stat-icon green"><Download size={18} /></div><div><span>Resources dumped</span><strong>284</strong></div><small>+18 today</small></div><div className="stat-card"><div className="stat-icon orange"><Clock3 size={18} /></div><div><span>Last activity</span><strong>12m</strong></div><small>new area</small></div><div className="stat-card"><div className="stat-icon blue"><HardDriveDownload size={18} /></div><div><span>Storage used</span><strong>2.4 GB</strong></div><small>of 10 GB</small></div></div>
        <div className="section-heading"><div><div className="title-line"><h2>Your targets</h2><span className="count">16 total</span></div><p>Manage your connected servers and start a new dump.</p></div><button className="primary-button" disabled={!apiConnected} onClick={() => setShowModal(true)}><Plus size={17} /> Add target</button></div>
        <div className="toolbar"><div className="search"><Search size={17} /><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search targets..." />{query && <button onClick={() => setQuery("")}><X size={14} /></button>}</div><div className="view-toggle"><button className="selected"><FolderKanban size={16} /></button><button><Terminal size={16} /></button></div></div>
        <div className="target-list">{filtered.map((target) => <div className="target-card" key={target.name}><div className="target-main"><div className="target-letter">{target.letter}</div><div><h3>{target.name}</h3><div className="target-meta"><span><Code2 size={13} /> {target.host}</span><span className="dot" /><span>{target.time}</span></div></div></div><div className="target-status"><span className={`status-text ${target.status === "Token found" ? "success" : ""}`}><i /> {target.status}</span><button className="secondary-button" disabled={!apiConnected} onClick={() => notify(`Dump started for ${target.name}`)}><Download size={15} /> Dump</button><button className="icon-button"><MoreHorizontal size={17} /></button></div></div>)}</div>
      </div>
    </section>
    {showModal && <div className="modal-backdrop" onClick={() => setShowModal(false)}><div className="modal" onClick={(e) => e.stopPropagation()}><div className="modal-header"><div><span className="kicker">NEW CONNECTION</span><h2>Add a target</h2></div><button className="icon-button" onClick={() => setShowModal(false)}><X size={18} /></button></div><label>Target name<input placeholder="My server" /></label><label>IP / CFX endpoint<input placeholder="Ex: cfx.re/join/xxxxxx" /></label><button className="primary-button full" onClick={() => { setShowModal(false); notify("Target added to your workspace") }}><Plus size={17} /> Add target</button></div></div>}
    {toast && <div className="toast"><ShieldCheck size={17} /> {toast}</div>}
    <style jsx global>{`button:disabled{opacity:.45;cursor:not-allowed}.status-chip.disconnected{color:#ff9b9b;border-color:#5b292f;background:#241417}.status-chip.connected{color:#7df0b2}.api-endpoint{display:inline-flex;align-items:center;gap:6px;margin-top:14px;color:#aaa8bb;font-family:DM Mono,monospace;font-size:11px}`}</style>
  </main>
}
