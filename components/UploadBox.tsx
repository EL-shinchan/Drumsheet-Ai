type UploadBoxProps = {
  onFileChange: (file: File | null) => void;
  selectedFile?: File | null;
  disabled?: boolean;
};

export default function UploadBox({ onFileChange, selectedFile, disabled }: UploadBoxProps) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <label htmlFor="audio-upload" className="mb-3 block text-sm font-semibold text-slate-200">
        Upload audio file
      </label>

      <input
        id="audio-upload"
        type="file"
        accept=".mp3,.wav,.m4a,.aac,.flac,audio/*"
        disabled={disabled}
        className="block w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-200 file:mr-4 file:rounded-lg file:border-0 file:bg-blue-600 file:px-4 file:py-2 file:text-white hover:file:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
        onChange={(e) => {
          const file = e.target.files?.[0] ?? null;
          onFileChange(file);
        }}
      />

      {selectedFile ? (
        <p className="mt-3 text-sm text-slate-400">
          Selected file: <span className="text-slate-200">{selectedFile.name}</span>
        </p>
      ) : null}
    </div>
  );
}
