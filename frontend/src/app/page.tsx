"use client";
import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import { api } from "@/lib/api";

type PricePoint = { date: string; close: number };
type Summary = {
  symbol: string;
  live_price: string;
  yesterday_price: string;
  price_30d_ago: string;
  price_1y_ago: string;
  exchange: string;
};

export default function Page() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [series, setSeries] = useState<PricePoint[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const s = await api<Summary>("/api/v1/prices/summary?symbol=RELIANCE&exchange=NSE");
        setSummary(s);
        const h = await api<PricePoint[]>("/api/v1/prices/history?symbol=RELIANCE&exchange=NSE");
        setSeries(h);
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
          <Stat label="Live" value={summary.live_price} />
          <Stat label="Prev Close" value={summary.yesterday_price} />
        </div>
      )}
      <div className="rounded-2xl border p-4">
        <h2 className="mb-2 font-medium">Reliance — Close Price</h2>
        <LineChart width={900} height={320} data={series}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" minTickGap={32} />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="close" dot={false} />
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
