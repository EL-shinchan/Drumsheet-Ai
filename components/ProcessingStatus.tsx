type ProcessingStatusProps = {
  message: string | null;
};

export default function ProcessingStatus({ message }: ProcessingStatusProps) {
  if (!message) return null;

  return (
    <div className="rounded-2xl border border-blue-900 bg-blue-950/40 p-5 text-sm font-medium text-blue-200">
      {message}
    </div>
  );
}
