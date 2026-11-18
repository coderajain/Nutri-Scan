import React, { useState, useEffect } from 'react';
import { Image as ImageIcon, FileText, Sparkles, Loader2, AlertCircle } from 'lucide-react';
import apiClient from '../api/client';

export const EvidenceViewer = ({ imageUrl, processedImageUrl, rawText, ocrConfidence }) => {
  const [activeTab, setActiveTab] = useState('image'); // 'image', 'processed', 'text'
  const [originalBlobUrl, setOriginalBlobUrl] = useState(null);
  const [processedBlobUrl, setProcessedBlobUrl] = useState(null);
  const [loadingImg, setLoadingImg] = useState(false);
  const [imgError, setImgError] = useState(false);

  // Securely load original image with JWT token via apiClient
  useEffect(() => {
    let isMounted = true;
    let objectUrl = null;

    if (imageUrl) {
      setLoadingImg(true);
      setImgError(false);

      apiClient
        .get(imageUrl, { responseType: 'blob' })
        .then((res) => {
          if (isMounted) {
            objectUrl = URL.createObjectURL(res.data);
            setOriginalBlobUrl(objectUrl);
            setLoadingImg(false);
          }
        })
        .catch((err) => {
          console.warn('Failed to fetch image via blob client:', err);
          if (isMounted) {
            // Fallback to direct URL if blob request fails
            setOriginalBlobUrl(imageUrl);
            setLoadingImg(false);
          }
        });
    }

    return () => {
      isMounted = false;
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [imageUrl]);

  // Load processed image if available
  useEffect(() => {
    let isMounted = true;
    let objectUrl = null;

    if (processedImageUrl) {
      apiClient
        .get(processedImageUrl, { responseType: 'blob' })
        .then((res) => {
          if (isMounted) {
            objectUrl = URL.createObjectURL(res.data);
            setProcessedBlobUrl(objectUrl);
          }
        })
        .catch(() => {
          if (isMounted) {
            setProcessedBlobUrl(processedImageUrl);
          }
        });
    }

    return () => {
      isMounted = false;
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [processedImageUrl]);

  const currentDisplayUrl = activeTab === 'processed' ? (processedBlobUrl || originalBlobUrl) : originalBlobUrl;

  return (
    <div className="bg-white rounded-3xl border border-slate-200 overflow-hidden shadow-xs">
      {/* Tab Navigation */}
      <div className="flex flex-wrap border-b border-slate-200 bg-slate-50 px-4 py-3 justify-between items-center gap-2">
        <div className="flex space-x-2">
          <button
            type="button"
            onClick={() => setActiveTab('image')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition ${
              activeTab === 'image'
                ? 'bg-white text-brand-700 shadow-xs border border-slate-200'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <ImageIcon className="h-4 w-4 text-brand-600" />
            <span>Original Evidence</span>
          </button>

          {processedImageUrl && (
            <button
              type="button"
              onClick={() => setActiveTab('processed')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition ${
                activeTab === 'processed'
                  ? 'bg-white text-purple-700 shadow-xs border border-slate-200'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Sparkles className="h-4 w-4 text-purple-600" />
              <span>Enhanced View</span>
            </button>
          )}

          <button
            type="button"
            onClick={() => setActiveTab('text')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition ${
              activeTab === 'text'
                ? 'bg-white text-slate-900 shadow-xs border border-slate-200'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <FileText className="h-4 w-4 text-metrology-600" />
            <span>Extracted OCR Text</span>
          </button>
        </div>

        {ocrConfidence !== null && ocrConfidence !== undefined && (
          <span className="text-xs font-semibold text-slate-600">
            OCR Confidence: <span className="font-bold text-slate-900">{ocrConfidence}%</span>
          </span>
        )}
      </div>

      {/* Content Area */}
      <div className="p-4 sm:p-6">
        {activeTab === 'image' || activeTab === 'processed' ? (
          <div className="flex justify-center items-center bg-slate-950/5 rounded-2xl p-4 min-h-[340px]">
            {loadingImg ? (
              <div className="flex flex-col items-center space-y-2 text-slate-500">
                <Loader2 className="h-8 w-8 animate-spin text-brand-600" />
                <span className="text-xs font-semibold">Loading preserved evidence...</span>
              </div>
            ) : currentDisplayUrl && !imgError ? (
              <img
                src={currentDisplayUrl}
                alt={activeTab === 'processed' ? 'Enhanced Packaging Evidence' : 'Preserved Packaging Evidence'}
                onError={() => setImgError(true)}
                className="max-h-[520px] w-auto object-contain rounded-xl shadow-sm border border-slate-200/80 bg-white"
              />
            ) : (
              <div className="text-slate-400 text-sm flex flex-col items-center space-y-2 py-8">
                <AlertCircle className="h-8 w-8 text-slate-400" />
                <span className="font-medium">Evidence image preview unavailable</span>
                <span className="text-xs text-slate-400">The uploaded file has been archived on disk.</span>
              </div>
            )}
          </div>
        ) : (
          <div className="bg-slate-900 text-slate-100 p-5 rounded-2xl font-mono text-xs overflow-x-auto max-h-[520px] whitespace-pre-wrap leading-relaxed select-all border border-slate-800">
            {rawText || '// No text extracted by OCR engine.'}
          </div>
        )}
      </div>
    </div>
  );
};

export default EvidenceViewer;
