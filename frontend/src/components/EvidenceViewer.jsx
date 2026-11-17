import React, { useState } from 'react';
import { Image as ImageIcon, FileText, ZoomIn } from 'lucide-react';

export const EvidenceViewer = ({ imageUrl, rawText, ocrConfidence }) => {
  const [activeTab, setActiveTab] = useState('image');

  return (
    <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-xs">
      <div className="flex border-b border-slate-200 bg-slate-50 px-4 py-3 justify-between items-center">
        <div className="flex space-x-2">
          <button
            onClick={() => setActiveTab('image')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition ${
              activeTab === 'image'
                ? 'bg-white text-slate-900 shadow-xs border border-slate-200'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <ImageIcon className="h-4 w-4 text-brand-600" />
            <span>Original Evidence</span>
          </button>
          <button
            onClick={() => setActiveTab('text')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition ${
              activeTab === 'text'
                ? 'bg-white text-slate-900 shadow-xs border border-slate-200'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <FileText className="h-4 w-4 text-metrology-600" />
            <span>Raw OCR Text</span>
          </button>
        </div>

        {ocrConfidence !== null && ocrConfidence !== undefined && (
          <span className="text-xs font-semibold text-slate-600">
            OCR Confidence: <span className="font-bold text-slate-900">{ocrConfidence}%</span>
          </span>
        )}
      </div>

      <div className="p-4">
        {activeTab === 'image' ? (
          <div className="flex justify-center items-center bg-slate-900/5 rounded-xl p-2 min-h-[320px]">
            {imageUrl ? (
              <img
                src={imageUrl}
                alt="Preserved Label Evidence"
                className="max-h-[480px] w-auto object-contain rounded-lg shadow-sm"
              />
            ) : (
              <div className="text-slate-400 text-sm flex flex-col items-center space-y-2">
                <ImageIcon className="h-8 w-8 text-slate-300" />
                <span>No physical evidence preview available</span>
              </div>
            )}
          </div>
        ) : (
          <div className="bg-slate-900 text-slate-100 p-4 rounded-xl font-mono text-xs overflow-x-auto max-h-[480px] whitespace-pre-wrap leading-relaxed select-all">
            {rawText || '// No text extracted by OCR engine.'}
          </div>
        )}
      </div>
    </div>
  );
};
export default EvidenceViewer;
