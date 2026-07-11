"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Zap } from "lucide-react";
import { login, setToken } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert } from "@/components/ui/alert";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("dana@acme.test");
  const [password, setPassword] = useState("password123");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const tok = await login(email, password);
      setToken(tok);
      router.push("/dashboard");
    } catch {
      setError("Invalid email or password. Try one of the demo users below.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50/30 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="flex items-center gap-2.5 mb-8 justify-center">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand shadow-md">
            <Zap className="h-5 w-5 text-white" />
          </div>
          <span className="text-2xl font-bold text-gray-900">Schedulr</span>
        </div>

        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8">
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Sign in</h2>
            <p className="text-sm text-gray-500 mt-1">
              Access your sales team workspace
            </p>
          </div>

          <form onSubmit={onSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                autoComplete="email"
                required
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                autoComplete="current-password"
                required
              />
            </div>

            {error && <Alert variant="error">{error}</Alert>}

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Signing in…" : "Sign in"}
            </Button>
          </form>
        </div>

        {/* Demo hint */}
        <div className="mt-4 rounded-xl bg-amber-50 border border-amber-200 px-4 py-3">
          <p className="text-xs font-medium text-amber-700 mb-1.5">Demo users (all pw: <code className="font-mono">password123</code>)</p>
          <div className="space-y-1">
            {[
              { label: "Dana Ortiz", email: "dana@acme.test", tz: "Chicago" },
              { label: "Lukas Berg", email: "lukas@acme.test", tz: "Berlin" },
              { label: "Mei Tan", email: "mei@acme.test", tz: "Singapore" },
            ].map(({ label, email: e, tz }) => (
              <button
                key={e}
                type="button"
                onClick={() => { setEmail(e); setPassword("password123"); }}
                className="block w-full text-left rounded px-2 py-0.5 text-xs text-amber-800 hover:bg-amber-100 transition-colors"
              >
                <span className="font-medium">{label}</span>
                <span className="text-amber-600 ml-1">({tz})</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
