"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Video, Mail, Lock, User, AlertCircle, Loader2, CheckCircle } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const PLANS = {
  free: { name: "Free", price: "$0", credits: 3, features: ["3 videos/month", "Stock visuals", "Standard voices", "Watermarked exports"] },
  pro: { name: "Pro", price: "$19/mo", credits: 50, features: ["50 videos/month", "Stock + AI visuals", "Premium voices", "No watermark", "Priority rendering"] },
  creator: { name: "Creator", price: "$49/mo", credits: 200, features: ["200 videos/month", "Unlimited AI visuals", "Voice cloning (soon)", "Custom fonts", "API access (beta)"] },
};

export default function RegisterPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get("redirect") || "/";
  const planParam = searchParams.get("plan") || "free";
  const [selectedPlan, setSelectedPlan] = useState(planParam);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const plan = PLANS[selectedPlan as keyof typeof PLANS] || PLANS.free;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/v1/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, name }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Registration failed");
      }

      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      router.push(redirectTo);
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4 py-12">
      <div className="w-full max-w-4xl">
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Plan Selection */}
          <div className="space-y-6">
            <div className="lg:hidden">
              <Link href="/" className="inline-flex items-center gap-2 font-display font-bold text-2xl text-primary mb-6">
                <Video className="w-8 h-8" />
                <span>VideoGen AI</span>
              </Link>
            </div>

            <div className="hidden lg:block text-center lg:text-left">
              <Link href="/" className="inline-flex items-center gap-2 font-display font-bold text-2xl text-primary mb-8">
                <Video className="w-8 h-8" />
                <span>VideoGen AI</span>
              </Link>
              <h1 className="font-display text-4xl font-bold mb-4">Create Your Account</h1>
              <p className="text-lg text-muted-foreground">
                Start creating AI-powered vertical videos in minutes
              </p>
            </div>

            <div className="space-y-3">
              {Object.entries(PLANS).map(([key, p]) => (
                <button
                  key={key}
                  onClick={() => setSelectedPlan(key)}
                  className={`w-full p-4 rounded-xl border-2 text-left transition-all ${
                    selectedPlan === key
                      ? "border-primary bg-primary/5 shadow-lg shadow-primary/10"
                      : "border-border hover:border-primary/50"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-semibold text-lg">{p.name}</div>
                      <div className="text-sm text-muted-foreground">{p.credits} credits/month</div>
                    </div>
                    <div className="text-right">
                      <div className="font-display font-bold text-xl">{p.price}</div>
                      {selectedPlan === key && (
                        <CheckCircle className="w-5 h-5 text-primary mx-auto mt-1" />
                      )}
                    </div>
                  </div>
                  <ul className="mt-3 space-y-1 text-sm text-muted-foreground">
                    {p.features.map((f, i) => (
                      <li key={i} className="flex items-center gap-2">
                        <CheckCircle className="w-3.5 h-3.5 text-primary/70 flex-shrink-0" />
                        {f}
                      </li>
                    ))}
                  </ul>
                </button>
              ))}
            </div>
          </div>

          {/* Registration Form */}
          <div className="bg-card border border-border rounded-2xl p-6 lg:p-8">
            <div className="hidden lg:block text-center mb-8">
              <h1 className="font-display text-3xl font-bold mb-2">Sign Up</h1>
              <p className="text-muted-foreground">Enter your details to get started</p>
            </div>

            {error && (
              <div className="mb-5 flex items-center gap-2 p-3 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive text-sm">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="space-y-2">
                <label htmlFor="name" className="block text-sm font-medium">
                  Name (optional)
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <input
                    id="name"
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                    placeholder="John Doe"
                    disabled={loading}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label htmlFor="email" className="block text-sm font-medium">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                    placeholder="you@example.com"
                    required
                    disabled={loading}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label htmlFor="password" className="block text-sm font-medium">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                    placeholder="•••••••• (min 8 chars)"
                    required
                    disabled={loading}
                    minLength={8}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label htmlFor="confirmPassword" className="block text-sm font-medium">
                  Confirm Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <input
                    id="confirmPassword"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                    placeholder="••••••••"
                    required
                    disabled={loading}
                  />
                </div>
              </div>

              <Button type="submit" className="w-full" disabled={loading} style={{ padding: "0.875rem" }}>
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin mr-2" />
                    Creating Account...
                  </>
                ) : (
                  `Create ${plan.name} Account`
                )}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-muted-foreground">
                Already have an account?{" "}
                <Link href={`/auth/login?redirect=${redirectTo}`} className="text-primary hover:underline font-medium">
                  Sign In
                </Link>
              </p>
            </div>

            <p className="mt-4 text-center text-xs text-muted-foreground">
              By creating an account, you agree to our{" "}
              <Link href="/terms" className="underline hover:text-foreground">Terms of Service</Link>
              {" and "}
              <Link href="/privacy" className="underline hover:text-foreground">Privacy Policy</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}