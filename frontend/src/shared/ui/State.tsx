export function LoadingState({ label = "Загрузка..." }: { label?: string }) {
  return <div className="state state-loading">{label}</div>;
}

export function ErrorState({ message }: { message: string }) {
  return <div className="state state-error">{message}</div>;
}

export function EmptyState({ message }: { message: string }) {
  return <div className="state state-empty">{message}</div>;
}

export function StatusPill({ value }: { value: string }) {
  return <span className={`pill pill-${value}`}>{value}</span>;
}
