'use client';

import { useEffect, useMemo, useState } from 'react';
import { api } from '@/lib/api';

type Product = { id: number; title: string; price: string; description: string; local_images: string[] };
type Template = { key: string; name: string; duration_seconds: number; scene_count: number };
type Job = { id: number; product_id: number; status: string; progress: number; error?: string; variant_index: number };
type ExportAsset = { id: number; caption: string; hashtags: string[]; hooks: string[]; ctas: string[]; location: string; filename: string };

type Voice = { tone: string; banned_phrases: string[]; preferred_ctas: string[] };

const nav = ['Library', 'Templates', 'Queue', 'Exports', 'Settings'] as const;

export default function Home() {
  const [tab, setTab] = useState<(typeof nav)[number]>('Library');
  const [products, setProducts] = useState<Product[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [exports, setExports] = useState<ExportAsset[]>([]);
  const [selected, setSelected] = useState<number[]>([]);
  const [templateKey, setTemplateKey] = useState('problem-product-benefit');
  const [variants, setVariants] = useState(3);
  const [voice, setVoice] = useState<Voice>({ tone: 'minimalist', banned_phrases: [], preferred_ctas: [] });

  async function refresh() {
    const [p, t, j, e, v] = await Promise.all([
      api<Product[]>('/products'),
      api<Template[]>('/templates'),
      api<Job[]>('/queue/jobs'),
      api<ExportAsset[]>('/exports'),
      api<Voice>('/brand-voice')
    ]);
    setProducts(p);
    setTemplates(t);
    setJobs(j);
    setExports(e);
    setVoice(v);
    if (t[0] && !templateKey) setTemplateKey(t[0].key);
  }

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 4000);
    return () => clearInterval(id);
  }, []);

  const selectedProducts = useMemo(() => products.filter((p) => selected.includes(p.id)), [products, selected]);

  async function uploadCsv(file: File) {
    const fd = new FormData();
    fd.append('file', file);
    await api('/import/csv', { method: 'POST', body: fd });
    refresh();
  }

  async function enqueue() {
    await api('/queue/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_ids: selected, template_key: templateKey, variants })
    });
    setTab('Queue');
    refresh();
  }

  async function updateVoice() {
    await api('/brand-voice', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: 1, ...voice })
    });
    refresh();
  }

  return (
    <main className="min-h-screen p-8">
      <div className="mx-auto grid max-w-7xl grid-cols-[220px_1fr] gap-8">
        <aside className="panel p-5 h-[85vh]">
          <h1 className="text-xl font-semibold tracking-tight">ClipForge</h1>
          <p className="text-muted text-sm mt-1">Ready-to-post short-form packs</p>
          <div className="mt-8 space-y-2">
            {nav.map((n) => (
              <button key={n} className={`w-full text-left rounded-xl px-3 py-2 ${tab === n ? 'bg-white text-black' : 'bg-white/5'}`} onClick={() => setTab(n)}>
                {n}
              </button>
            ))}
          </div>
        </aside>
        <section className="space-y-4">
          {tab === 'Library' && (
            <div className="space-y-4">
              <div className="panel p-4 flex items-center justify-between">
                <label className="btn-secondary cursor-pointer">Import CSV<input hidden type="file" accept=".csv" onChange={(e) => e.target.files?.[0] && uploadCsv(e.target.files[0])} /></label>
                <button className="btn" onClick={enqueue} disabled={!selected.length}>Generate Selected ({selected.length})</button>
              </div>
              <div className="grid grid-cols-3 gap-4">
                {products.map((p) => (
                  <div className="panel p-4" key={p.id}>
                    <div className="aspect-[9/12] rounded-xl bg-white/5 mb-3 overflow-hidden">
                      {p.local_images?.[0] ? <img src={`http://localhost:8000/${p.local_images[0]}`} className="w-full h-full object-cover" /> : <div className="w-full h-full grid place-items-center text-muted">No image</div>}
                    </div>
                    <p className="font-medium line-clamp-2">{p.title}</p>
                    <p className="text-accent">${p.price}</p>
                    <label className="text-sm mt-2 flex gap-2"><input type="checkbox" checked={selected.includes(p.id)} onChange={(e) => setSelected(e.target.checked ? [...selected, p.id] : selected.filter((id) => id !== p.id))} /> Select</label>
                  </div>
                ))}
              </div>
            </div>
          )}

          {tab === 'Templates' && (
            <div className="grid grid-cols-3 gap-4">
              {templates.map((t) => (
                <div key={t.key} className={`panel p-5 ${templateKey === t.key ? 'ring-2 ring-accent' : ''}`}>
                  <h3 className="font-semibold">{t.name}</h3>
                  <p className="text-sm text-muted mt-2">{t.scene_count} scenes · {t.duration_seconds}s</p>
                  <button className="btn-secondary mt-4" onClick={() => setTemplateKey(t.key)}>Use template</button>
                </div>
              ))}
            </div>
          )}

          {tab === 'Queue' && (
            <div className="panel p-5 space-y-3">
              <div className="flex items-center gap-3">
                <span className="text-sm text-muted">Variant Generator</span>
                <input className="input w-24" type="number" min={1} max={3} value={variants} onChange={(e) => setVariants(Number(e.target.value))} />
              </div>
              {jobs.map((j) => (
                <div key={j.id} className="rounded-xl bg-white/5 p-3">
                  <p>Job #{j.id} · Product {j.product_id} · Variant {j.variant_index}</p>
                  <p className="text-sm text-muted">{j.status} · {(j.progress * 100).toFixed(0)}% {j.error ? `· ${j.error}` : ''}</p>
                </div>
              ))}
            </div>
          )}

          {tab === 'Exports' && (
            <div className="space-y-4">
              {exports.map((e) => (
                <div key={e.id} className="panel p-5 grid grid-cols-[220px_1fr] gap-4">
                  <video controls src={`http://localhost:8000/${e.location}`} className="rounded-xl bg-black h-64" />
                  <div>
                    <p className="font-medium">{e.filename}</p>
                    <p className="text-sm mt-2">{e.caption}</p>
                    <p className="text-sm text-muted mt-1">{e.hashtags.join(' ')}</p>
                    <p className="text-sm mt-3">Hooks: {e.hooks.join(' • ')}</p>
                    <p className="text-sm">CTAs: {e.ctas.join(' • ')}</p>
                    <a className="btn-secondary inline-block mt-4" href={`http://localhost:8000/${e.location}`} download>Download MP4</a>
                  </div>
                </div>
              ))}
            </div>
          )}

          {tab === 'Settings' && (
            <div className="panel p-5 space-y-3 max-w-2xl">
              <p className="text-sm text-muted">Brand Voice</p>
              <select className="input" value={voice.tone} onChange={(e) => setVoice({ ...voice, tone: e.target.value })}>
                <option>minimalist</option><option>playful</option><option>luxury</option><option>direct-response</option>
              </select>
              <textarea className="input h-28" value={voice.banned_phrases.join(',')} onChange={(e) => setVoice({ ...voice, banned_phrases: e.target.value.split(',').map((v) => v.trim()).filter(Boolean) })} placeholder="Banned phrases (comma separated)" />
              <textarea className="input h-24" value={voice.preferred_ctas.join(',')} onChange={(e) => setVoice({ ...voice, preferred_ctas: e.target.value.split(',').map((v) => v.trim()).filter(Boolean) })} placeholder="Preferred CTA list" />
              <button className="btn" onClick={updateVoice}>Save Voice</button>
              <p className="text-xs text-muted">Music track uploads accept only user-provided files in supported formats. No copyrighted bundled tracks included.</p>
            </div>
          )}

          {!!selectedProducts.length && tab !== 'Library' && <div className="text-xs text-muted">Selected: {selectedProducts.map((p) => p.title).join(', ')}</div>}
        </section>
      </div>
    </main>
  );
}
