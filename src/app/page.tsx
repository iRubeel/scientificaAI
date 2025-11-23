import UploadZone from "@/components/UploadZone";

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-start min-h-[calc(100vh-4rem)] p-6 sm:p-20 gap-16 pt-24">
      <div className="text-center space-y-6 max-w-3xl animate-in fade-in slide-in-from-top-8 duration-700">
        <div className="inline-flex items-center rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary backdrop-blur-xl shadow-sm">
          <span>AI Scientifica v0.1</span>
        </div>
        <h1 className="text-5xl sm:text-7xl font-bold tracking-tight bg-gradient-to-b from-white via-white/90 to-white/50 bg-clip-text text-transparent drop-shadow-sm">
          Scientific Truth Verification
        </h1>
        <p className="text-lg sm:text-xl text-muted-foreground leading-relaxed max-w-2xl mx-auto">
          Upload any math or physics paper. We'll extract the core theorems and
          translate them into formal logic for verification.
        </p>
      </div>

      <div className="w-full animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-200 fill-mode-forwards">
        <UploadZone />
      </div>
    </div>
  );
}
