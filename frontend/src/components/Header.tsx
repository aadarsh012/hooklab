export default function Header() {
  return (
    <header className="shrink-0 flex items-center justify-between px-6 py-4 border-b border-[#2a2a2a]">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-green-400 rounded-lg flex items-center justify-center text-black font-bold text-sm">
          H
        </div>
        <div>
          <div className="font-semibold text-white leading-tight">HookLab</div>
          <div className="text-xs text-gray-500 leading-tight">private practice room</div>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <button className="px-4 py-1.5 border border-[#3a3a3a] rounded-lg text-sm text-gray-300 hover:border-gray-500 hover:text-white transition-colors">
          Library
        </button>
        <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center text-white text-[10px] font-semibold">
          YOU
        </div>
      </div>
    </header>
  );
}
