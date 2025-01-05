import { useState } from 'react';
import { Menu, Info, Settings } from 'lucide-react';

const SidePanel = () => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className={`fixed left-0 top-0 h-full bg-[#0066d3] text-white transition-all duration-300 ${isExpanded ? 'w-64' : 'w-16'}`}>
      <button 
        onClick={() => setIsExpanded(!isExpanded)} 
        className="w-full p-4 hover:bg-blue-700"
      >
        <Menu size={24} />
      </button>
      
      <div className="flex flex-col gap-4 p-4">
        {isExpanded ? (
          <>
            <button className="flex items-center gap-2 text-left hover:bg-blue-700 p-2 rounded">
              <span className="text-xl font-bold">New chat</span>
            </button>
            
            <div className="mt-4">
              <h2 className="text-lg font-semibold mb-2">Recent</h2>
              <div className="text-gray-200">Recent</div>
            </div>
          </>
        ) : (
          <button className="hover:bg-blue-700 p-2 rounded">
            +
          </button>
        )}
      </div>

      <div className="absolute bottom-0 left-0 w-full p-4">
        <button className="flex items-center gap-2 w-full hover:bg-blue-700 p-2 rounded mb-2">
          <Info size={20} />
          {isExpanded && <span>About JuanGPT</span>}
        </button>
        <button className="flex items-center gap-2 w-full hover:bg-blue-700 p-2 rounded">
          <Settings size={20} />
          {isExpanded && <span>Settings</span>}
        </button>
      </div>
    </div>
  );
};

export default SidePanel;