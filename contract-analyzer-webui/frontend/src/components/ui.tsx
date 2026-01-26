import React from "react";

export function cn(...classes: Array<string | undefined | false | null>) {
  return classes.filter(Boolean).join(" ");
}

export function Card(props: React.PropsWithChildren<{ className?: string }>) {
  return (
    <div className={cn("rounded-2xl border border-white/10 bg-white/5 shadow-xl shadow-black/20", props.className)}>
      {props.children}
    </div>
  );
}

export function CardHeader(props: React.PropsWithChildren<{ className?: string }>) {
  return <div className={cn("p-6 border-b border-white/10", props.className)}>{props.children}</div>;
}

export function CardContent(props: React.PropsWithChildren<{ className?: string }>) {
  return <div className={cn("p-6", props.className)}>{props.children}</div>;
}

export function Button(props: React.PropsWithChildren<{
  className?: string;
  variant?: "primary" | "secondary" | "ghost";
  disabled?: boolean;
  onClick?: () => void;
  type?: "button" | "submit";
}>) {
  const variant = props.variant ?? "primary";
  const cls =
    variant === "primary"
      ? "bg-white text-black hover:bg-white/90"
      : variant === "secondary"
        ? "bg-white/10 text-white hover:bg-white/15 border border-white/10"
        : "bg-transparent hover:bg-white/10 text-white";
  return (
    <button
      type={props.type ?? "button"}
      disabled={props.disabled}
      onClick={props.onClick}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold transition disabled:opacity-40 disabled:cursor-not-allowed",
        cls,
        props.className
      )}
    >
      {props.children}
    </button>
  );
}

export function Badge(props: React.PropsWithChildren<{ className?: string; tone?: "green" | "red" | "gray" | "yellow" }>) {
  const tone = props.tone ?? "gray";
  const toneCls =
    tone === "green"
      ? "bg-emerald-500/15 text-emerald-200 border-emerald-500/20"
      : tone === "red"
        ? "bg-rose-500/15 text-rose-200 border-rose-500/20"
        : tone === "yellow"
          ? "bg-amber-500/15 text-amber-200 border-amber-500/20"
          : "bg-white/10 text-white/80 border-white/10";
  return (
    <span className={cn("inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium", toneCls, props.className)}>
      {props.children}
    </span>
  );
}

export function Input(props: React.InputHTMLAttributes<HTMLInputElement> & { className?: string }) {
  return (
    <input
      {...props}
      className={cn(
        "w-full rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm text-white placeholder:text-white/40 outline-none focus:ring-2 focus:ring-white/20",
        props.className
      )}
    />
  );
}
