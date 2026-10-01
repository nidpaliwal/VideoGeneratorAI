"use client";

import { useEffect, useState } from "react";
import { MediaPreview } from "@/components/media/MediaPreview";
import { Shield, Video, Sparkles } from "lucide-react";

export default function MediaDemoPage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [checkingAuth, setCheckingAuth] = useState(true);

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem("access_token");
      setIsAuthenticated(!!token);
      setCheckingAuth(false);
    };
    checkAuth();
  }, []);

  if (checkingAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Checking authentication...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <div className="max-w-md w-full text-center">
          <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-primary/10 flex items-center justify-center">
            <Video className="w-8 h-8 text-primary" />
          </div>
          <h1 className="font-display text-3xl font-bold mb-4">Media Library Demo</h1>
          <p className="text-muted-foreground mb-8">
            Please sign in to access the media library and test Cloudinary integration.
          </p>
          <div className="space-y-3">
            <a href="/auth/login" className="btn btn-primary w-full">
              Sign In
            </a>
            <a href="/auth/register" className="btn btn-outline w-full">
              Create Account
            </a>
          </div>
          <div className="mt-8 p-4 bg-muted rounded-xl text-left">
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary" />
              What you can do:
            </h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li className="flex items-center gap-2"><Video className="w-4 h-4" /> Upload videos and images to Cloudinary</li>
              <li className="flex items-center gap-2"><Video className="w-4 h-4" /> Apply 9:16 vertical crop transformations</li>
              <li className="flex items-center gap-2"><Video className="w-4 h-4" /> Add text overlay watermarks</li>
              <li className="flex items-center gap-2"><Video className="w-4 h-4" /> Auto quality/format optimization (f_auto, q_auto)</li>
              <li className="flex items-center gap-2"><Video className="w-4 h-4" /> Preview transformations in real-time</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b border-border sticky top-0 z-50 bg-background/95 backdrop-blur-sm">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <a href="/" className="flex items-center gap-2 font-display font-bold text-xl text-primary">
            <Video className="w-6 h-6" />
            <span>VideoGen AI</span>
          </a>
          <div className="flex items-center gap-4">
            <a href="/" className="btn btn-ghost btn-sm">Back to Home</a>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <h1 className="font-display text-3xl md:text-4xl font-bold mb-3">Cloudinary Media Library</h1>
            <p className="text-lg text-muted-foreground">
              Test the Cloudinary integration with real-time transformations, 9:16 vertical crops,
              and free-plan watermarks.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-4 mb-8">
            <div className="p-4 bg-card border border-border rounded-xl">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Video className="w-5 h-5 text-primary" />
                </div>
                <h3 className="font-semibold">Video Transformations</h3>
              </div>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>9:16 vertical crop (c_fill, ar_9:16, g_auto)</li>
                <li>Auto quality & format (f_auto, q_auto)</li>
                <li>Text overlay watermarks</li>
                <li>Blur, scale, and custom effects</li>
              </ul>
            </div>
            <div className="p-4 bg-card border border-border rounded-xl">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Shield className="w-5 h-5 text-primary" />
                </div>
                <h3 className="font-semibold">Free Plan Features</h3>
              </div>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>Watermark via text overlay</li>
                <li>No fake ?watermark=1 URLs</li>
                <li>Real Cloudinary transformations</li>
                <li>Delivery optimization</li>
              </ul>
            </div>
            <div className="p-4 bg-card border border-border rounded-xl">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-primary" />
                </div>
                <h3 className="font-semibold">Media Management</h3>
              </div>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>List/upload/delete media</li>
                <li>Signed upload URLs for direct upload</li>
                <li>Resource metadata & thumbnails</li>
                <li>Per-user folder isolation</li>
              </ul>
            </div>
          </div>

          <MediaPreview />
        </div>
      </main>
    </div>
  );
}