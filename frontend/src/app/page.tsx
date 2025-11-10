"use client";
import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import { api } from "@/lib/api";

type Summary = {
  symbol: string;
  live_price: string | number;
  yesterday_price: string | number;
  price_30d_ago: string | number;
  price_1y_ago: string | number;
  exchange: string;
};

type PricePoint = { label: string; value: number };

export default function Page() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [series, setSeries] = useState<PricePoint[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        // ✅ match your backend route
        // if your backend expects exchange, try the second line instead
        const s = await api<Summary>("/api/v1/prices/RELIANCE");
        // const s = await api<Summary>("/api/v1/prices/RELIANCE?exchange=NSE");

        setSummary(s);

        // Build a 4-point pseudo-history from summary fields
        const n = (x: string | number | undefined) =>
          typeof x === "string" ? parseFloat(x) : (x ?? 0);

        const points: PricePoint[] = [
          { label: "1y ago", value: n(s.price_1y_ago) },
          { label: "30d ago", value: n(s.price_30d_ago) },
          { label: "yesterday", value: n(s.yesterday_price) },
          { label: "today", value: n(s.live_price) },
        ];
        setSeries(points);
      } catch (e: any) {
        setError(e?.message ?? "Failed to load");
      }
    })();
  }, []);

  return (
    <main className="p-6 space-y-6">
      <h1 className="text-2xl font-semibold">MyFinStocks Dashboard</h1>
      {error && <div className="rounded-xl border p-3 text-red-600">{error}</div>}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Stat label="Symbol" value={summary.symbol} />
          <Stat label="Exchange" value={summary.exchange} />
          <Stat label="Live" value={String(summary.live_price)} />
          <Stat label="Prev Close" value={String(summary.yesterday_price)} />
        </div>
      )}
      <div className="rounded-2xl border p-4">
        <h2 className="mb-2 font-medium">
          Reliance — Trend (1y → 30d → yesterday → today)
        </h2>
        <LineChart width={900} height={320} data={series}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="label" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="value" dot={false} />
        </LineChart>
      </div>
    </main>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border p-4">
      <div className="text-xs text-gray-500">{label}</div>
      <div className="text-lg font-semibold">{value}</div>
    </div>
  );
}