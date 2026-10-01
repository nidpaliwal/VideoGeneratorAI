"use client";

import { useState, useCallback } from "react";
import { Video, Image, FileVideo, Download, ExternalLink, Loader2, AlertTriangle } from "lucide-react";

interface MediaItem {
  public_id: string;
  url: string;
  secure_url: string;
  resource_type: "video" | "image" | "raw";
  format: string;
  width?: number;
  height?: number;
  duration?: number;
  bytes: number;
  created_at: string;
  folder: string;
  tags: string[];
}

interface MediaListResponse {
  items: MediaItem[];
  total: number;
  page: number;
  page_size: number;
  next_cursor: string | null;
}

interface UploadResponse {
  public_id: string;
  url: string;
  secure_url: string;
  resource_type: string;
  format: string;
  width?: number;
  height?: number;
  duration?: number;
  bytes: number;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  const token = localStorage.getItem("access_token");
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export function MediaPreview() {
  const [mediaItems, setMediaItems] = useState<MediaItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [selectedMedia, setSelectedMedia] = useState<MediaItem | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [resourceType, setResourceType] = useState<"video" | "image">("video");
  const [showTransformations, setShowTransformations] = useState(false);
  const [transformations, setTransformations] = useState<Record<string, any>>({});

  const loadMedia = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchWithAuth(`/api/v1/media?resource_type=${resourceType}&page=${page}&page_size=20`);
      setMediaItems(data.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load media");
    } finally {
      setLoading(false);
    }
  }, [resourceType, page]);

  const handleUpload = async (file: File) => {
    setUploading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("resource_type", resourceType);
      formData.append("folder", "videogen/uploads");

      const token = localStorage.getItem("access_token");
      const response = await fetch(`${API_URL}/api/v1/media/upload`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Upload failed" }));
        throw new Error(error.detail || "Upload failed");
      }

      await loadMedia();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleUpload(file);
      e.target.value = "";
    }
  };

  const handlePreview = (item: MediaItem) => {
    setSelectedMedia(item);
  };

  const handleClosePreview = () => {
    setSelectedMedia(null);
  };

  const handleTransformationPreview = async (item: MediaItem) => {
    const transforms = transformations[item.public_id] || [];
    try {
      const data = await fetchWithAuth("/api/v1/media/preview/" + encodeURIComponent(item.public_id), {
        method: "POST",
        body: JSON.stringify({ transformations: transforms, resource_type: item.resource_type }),
      });
      return data.preview_url;
    } catch {
      return item.secure_url;
    }
  };

  const applyTransformation = async (item: MediaItem, transform: Record<string, any>) => {
    const current = transformations[item.public_id] || [];
    setTransformations({ ...transformations, [item.public_id]: [...current, transform] });
  };

  const clearTransformations = (item: MediaItem) => {
    const newTransforms = { ...transformations };
    delete newTransforms[item.public_id];
    setTransformations(newTransforms);
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return "N/A";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const getResourceIcon = (type: string) => {
    switch (type) {
      case "video":
        return <Video className="w-5 h-5 text-primary" />;
      case "image":
        return <Image className="w-5 h-5 text-primary" />;
      default:
        return <FileVideo className="w-5 h-5 text-primary" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="font-display text-2xl font-bold">Media Library</h2>
          <p className="text-sm text-muted-foreground">
            Manage your uploaded videos, images, and rendered outputs
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex border border-border rounded-lg overflow-hidden">
            <button
              onClick={() => setResourceType("video")}
              className={`px-3 py-2 text-sm font-medium transition-colors ${
                resourceType === "video"
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Videos
            </button>
            <button
              onClick={() => setResourceType("image")}
              className={`px-3 py-2 text-sm font-medium transition-colors ${
                resourceType === "image"
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Images
            </button>
          </div>
          <label className="relative cursor-pointer">
            <input
              type="file"
              accept={resourceType === "video" ? "video/*" : "image/*"}
              onChange={handleFileSelect}
              className="sr-only"
            />
            <button
              disabled={uploading}
              className="btn btn-primary gap-2"
            >
              <Loader2 className={`w-4 h-4 ${uploading ? "animate-spin" : ""}`} />
              Upload
            </button>
          </label>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-4 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive text-sm">
          <AlertTriangle className="w-4 h-4" />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      ) : mediaItems.length === 0 ? (
        <div className="text-center py-12 border-2 border-dashed border-border rounded-xl">
          <Video className="w-12 h-12 mx-auto text-muted-foreground/50 mb-4" />
          <p className="text-muted-foreground">No media files yet</p>
          <p className="text-sm text-muted-foreground/70 mt-1">Upload a file or render a video to get started</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {mediaItems.map((item) => (
            <MediaCard
              key={item.public_id}
              item={item}
              onPreview={handlePreview}
              onTransform={applyTransformation}
              onClearTransforms={clearTransformations}
              transformations={transformations[item.public_id] || []}
            />
          ))}
        </div>
      )}

      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Page {page} • {mediaItems.length} items
        </p>
        <div className="flex gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1 || loading}
            className="btn btn-outline btn-sm"
          >
            Previous
          </button>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={mediaItems.length < 20 || loading}
            className="btn btn-outline btn-sm"
          >
            Next
          </button>
        </div>
      </div>

      {selectedMedia && (
        <MediaModal
          media={selectedMedia}
          onClose={handleClosePreview}
          onTransform={applyTransformation}
          onClearTransforms={clearTransformations}
          transformations={transformations[selectedMedia.public_id] || []}
        />
      )}
    </div>
  );
}

function MediaCard({
  item,
  onPreview,
  onTransform,
  onClearTransforms,
  transformations,
}: {
  item: MediaItem;
  onPreview: (item: MediaItem) => void;
  onTransform: (item: MediaItem, transform: Record<string, any>) => void;
  onClearTransforms: (item: MediaItem) => void;
  transformations: Record<string, any>[];
}) {
  const isVideo = item.resource_type === "video";
  const thumbnailUrl = isVideo
    ? `${item.secure_url.replace("/upload/", "/upload/w_400,h_711,c_fill,g_auto,ar_9:16,f_auto,q_auto/")}`
    : `${item.secure_url.replace("/upload/", "/upload/w_400,h_400,c_fill,g_auto,f_auto,q_auto/")}`;

  return (
    <div className="group relative bg-card border border-border rounded-xl overflow-hidden transition-all hover:border-primary/50 hover:shadow-lg">
      <div className="aspect-[9/16] relative bg-muted overflow-hidden">
        {isVideo ? (
          <video
            src={thumbnailUrl}
            className="w-full h-full object-cover"
            muted
            preload="metadata"
            playsInline
          />
        ) : (
          <img src={thumbnailUrl} alt={item.public_id} className="w-full h-full object-cover" />
        )}
        <div className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
          <button
            onClick={() => onPreview(item)}
            className="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center text-white group-hover:bg-white/30 transition-colors"
          >
            <Video className="w-6 h-6 ml-1" />
          </button>
        </div>
        {transformations.length > 0 && (
          <div className="absolute top-2 right-2">
            <span className="px-2 py-1 bg-primary/90 text-primary-foreground text-xs rounded-full">
              {transformations.length} transform{transformations.length > 1 ? "s" : ""}
            </span>
          </div>
        )}
        <div className="absolute bottom-2 left-2 right-2 flex justify-between">
          <span className="px-2 py-1 bg-black/70 text-white text-xs rounded">
            {formatBytes(item.bytes)}
          </span>
          {isVideo && item.duration && (
            <span className="px-2 py-1 bg-black/70 text-white text-xs rounded">
              {formatDuration(item.duration)}
            </span>
          )}
        </div>
      </div>
      <div className="p-3 space-y-2">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium truncate">{item.public_id.split("/").pop()}</p>
            <p className="text-xs text-muted-foreground">
              {item.format ? item.format.toUpperCase() : "MEDIA"} • {item.width}×{item.height}
            </p>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={(e) => { e.stopPropagation(); onTransform(item, { width: 1080, height: 1920, crop: "fill", gravity: "auto", aspect_ratio: "9:16" }); }}
              className="p-1.5 text-muted-foreground hover:text-foreground transition-colors"
              title="9:16 Vertical Crop"
            >
              <Video className="w-4 h-4" />
            </button>
            {isVideo && (
              <button
                onClick={(e) => { e.stopPropagation(); onTransform(item, { overlay: { font_family: "Arial", font_size: 60, font_weight: "bold", text: "VideoGen AI", color: "white", opacity: 30 }, gravity: "south_east", x: 20, y: 20 }); }}
                className="p-1.5 text-muted-foreground hover:text-foreground transition-colors"
                title="Add Watermark"
              >
                <Video className="w-4 h-4" />
              </button>
            )}
            <button
              onClick={(e) => { e.stopPropagation(); onClearTransforms(item); }}
              disabled={transformations.length === 0}
              className="p-1.5 text-muted-foreground hover:text-destructive transition-colors opacity-50"
              title="Clear Transformations"
            >
              <span className="text-xs font-bold">✕</span>
            </button>
          </div>
        </div>
        <div className="flex items-center justify-between pt-2 border-t border-border">
          <span className="text-xs text-muted-foreground">
            {new Date(item.created_at).toLocaleDateString()}
          </span>
          <a
            href={item.secure_url}
            target="_blank"
            rel="noopener noreferrer"
            className="p-1.5 text-muted-foreground hover:text-foreground transition-colors"
            title="Open in Cloudinary"
          >
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>
  );
}

function MediaModal({
  media,
  onClose,
  onTransform,
  onClearTransforms,
  transformations,
}: {
  media: MediaItem;
  onClose: () => void;
  onTransform: (item: MediaItem, transform: Record<string, any>) => void;
  onClearTransforms: (item: MediaItem) => void;
  transformations: Record<string, any>[];
}) {
  const isVideo = media.resource_type === "video";
  const previewUrl = isVideo
    ? media.secure_url.replace("/upload/", "/upload/w_1080,h_1920,c_fill,g_auto,ar_9:16,f_auto,q_auto/")
    : media.secure_url.replace("/upload/", "/upload/w_1080,h_1920,c_fill,g_auto,f_auto,q_auto/");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4">
      <div className="relative w-full max-w-4xl max-h-[90vh] bg-card rounded-xl overflow-hidden">
        <div className="flex items-center justify-between p-4 border-b border-border">
          <h3 className="font-semibold truncate">{media.public_id.split("/").pop()}</h3>
          <div className="flex items-center gap-2">
            {transformations.length > 0 && (
              <button
                onClick={() => onClearTransforms(media)}
                className="btn btn-sm btn-outline text-destructive hover:bg-destructive/10"
              >
                Clear Transforms
              </button>
            )}
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-muted transition-colors"
            >
              <span className="text-xl">✕</span>
            </button>
          </div>
        </div>
        <div className="p-4 aspect-[9/16] max-h-[60vh] bg-muted relative">
          {isVideo ? (
            <video
              src={previewUrl}
              className="w-full h-full object-contain"
              controls
              playsInline
            />
          ) : (
            <img src={previewUrl} alt={media.public_id} className="w-full h-full object-contain" />
          )}
        </div>
        <div className="p-4 border-t border-border space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground">Format</p>
              <p className="font-medium">{media.format ? media.format.toUpperCase() : "IMAGE"}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Dimensions</p>
              <p className="font-medium">{media.width}×{media.height}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Size</p>
              <p className="font-medium">{formatBytes(media.bytes)}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Duration</p>
              <p className="font-medium">{media.duration ? formatDuration(media.duration) : "N/A"}</p>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => onTransform(media, { width: 1080, height: 1920, crop: "fill", gravity: "auto", aspect_ratio: "9:16" })}
              className="btn btn-sm btn-outline"
            >
              9:16 Vertical Crop
            </button>
            <button
              onClick={() => onTransform(media, { quality: "auto", fetch_format: "auto" })}
              className="btn btn-sm btn-outline"
            >
              Auto Quality/Format
            </button>
            {isVideo && (
              <button
                onClick={() => onTransform(media, { overlay: { font_family: "Arial", font_size: 60, font_weight: "bold", text: "VideoGen AI", color: "white", opacity: 30 }, gravity: "south_east", x: 20, y: 20 })}
                className="btn btn-sm btn-outline"
              >
                Add Watermark
              </button>
            )}
            <button
              onClick={() => onTransform(media, { width: 540, height: 960, crop: "fill", gravity: "auto", aspect_ratio: "9:16" })}
              className="btn btn-sm btn-outline"
            >
              50% Scale
            </button>
            <button
              onClick={() => onTransform(media, { effect: "blur:20" })}
              className="btn btn-sm btn-outline"
            >
              Blur Effect
            </button>
          </div>
          {transformations.length > 0 && (
            <div className="p-3 bg-muted rounded-lg">
              <p className="text-sm font-medium mb-2">Applied Transformations:</p>
              <pre className="text-xs text-muted-foreground overflow-auto max-h-32">
                {JSON.stringify(transformations, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}