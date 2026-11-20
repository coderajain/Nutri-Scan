import React, { useState, useEffect } from 'react';
import { Image as ImageIcon, FileText, Sparkles, Loader2, AlertCircle, Layers } from 'lucide-react';
import apiClient, { getFullMediaUrl } from '../api/client';

export const EvidenceViewer = ({
  imageUrl,
  processedImageUrl,
  evidenceImages = [],
  rawText,
  ocrConfidence,
}) => {
  const [activeTab, setActiveTab] = useState('image'); // 'image', 'processed', 'text'
  const [selectedFaceIdx, setSelectedFaceIdx] = useState(0);
  const [originalBlobUrl, setOriginalBlobUrl] = useState(null);
  const [processedBlobUrl, setProcessedBlobUrl] = useState(null);
  const [loadingImg, setLoadingImg] = useState(false);
  const [imgError, setImgError] = useState(false);

  // Normalize faces list
  const faces = evidenceImages && evidenceImages.length > 0 ? evidenceImages : (imageUrl ? [imageUrl] : []);
  const activeImageUrl = faces[selectedFaceIdx] || imageUrl;
  const activeProcUrl = processedImageUrl
    ? (selectedFaceIdx === 0 ? processedImageUrl : `${processedImageUrl}?index=${selectedFaceIdx}`)
    : null;

  // Securely load original image with JWT token via apiClient
  useEffect(() => {
    let isMounted = true;
    let objectUrl = null;

    if (activeImageUrl) {
      setLoadingImg(true);
      setImgError(false);

      // Strip leading /api/v1 if present to avoid duplicate paths with apiClient baseURL
      const requestUrl = activeImageUrl.startsWith('/api/v1/')
        ? activeImageUrl.replace(/^\/api\/v1/, '')
        : activeImageUrl;

      apiClient
        .get(requestUrl, { responseType: 'blob' })
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
            setOriginalBlobUrl(getFullMediaUrl ? getFullMediaUrl(activeImageUrl) : activeImageUrl);
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
  }, [activeImageUrl]);

  // Load processed image if available
  useEffect(() => {
    let isMounted = true;
    let objectUrl = null;

    if (activeProcUrl) {
      const requestProcUrl = activeProcUrl.startsWith('/api/v1/')
        ? activeProcUrl.replace(/^\/api\/v1/, '')
        : activeProcUrl;

      apiClient
        .get(requestProcUrl, { responseType: 'blob' })
        .then((res) => {
          if (isMounted) {
            objectUrl = URL.createObjectURL(res.data);
            setProcessedBlobUrl(objectUrl);
          }
        })
        .catch(() => {
          if (isMounted) {
            setProcessedBlobUrl(getFullMediaUrl ? getFullMediaUrl(activeProcUrl) : activeProcUrl);
          }
        });
    }

    return () => {
      isMounted = false;
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [activeProcUrl]);

  const currentDisplayUrl = activeTab === 'processed' ? (processedBlobUrl || originalBlobUrl) : originalBlobUrl;

  return (
    <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-xs transition-colors">
      {/* Tab Navigation */}
      <div className="flex flex-wrap border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-850 px-4 py-3 justify-between items-center gap-2">
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex space-x-1.5 bg-slate-200/60 dark:bg-slate-800 p-1 rounded-xl">
            <button
              type="button"
              onClick={() => setActiveTab('image')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                activeTab === 'image'
                  ? 'bg-white dark:bg-slate-700 text-brand-700 dark:text-brand-300 shadow-xs'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <ImageIcon className="h-4 w-4 text-brand-600 dark:text-brand-400" />
              <span>Preserved Evidence</span>
            </button>

            {processedImageUrl && (
              <button
                type="button"
                onClick={() => setActiveTab('processed')}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                  activeTab === 'processed'
                    ? 'bg-white dark:bg-slate-700 text-purple-700 dark:text-purple-300 shadow-xs'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <Sparkles className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                <span>Enhanced View</span>
              </button>
            )}

            <button
              type="button"
              onClick={() => setActiveTab('text')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                activeTab === 'text'
                  ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <FileText className="h-4 w-4 text-metrology-600 dark:text-metrology-400" />
              <span>Combined OCR Text</span>
            </button>
          </div>

          {/* Multiple Faces Selector */}
          {faces.length > 1 && (
            <div className="flex items-center space-x-1 pl-2 border-l border-slate-200 dark:border-slate-700">
              <Layers className="h-3.5 w-3.5 text-slate-400 dark:text-slate-500 mr-1" />
              {faces.map((_, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setSelectedFaceIdx(idx)}
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition ${
                    selectedFaceIdx === idx
                      ? 'bg-brand-600 text-white shadow-xs'
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'
                  }`}
                >
                  Face {idx + 1}
                </button>
              ))}
            </div>
          )}
        </div>

        {ocrConfidence !== null && ocrConfidence !== undefined && (
          <span className="text-xs font-semibold text-slate-600 dark:text-slate-400">
            OCR Confidence: <span className="font-bold text-slate-900 dark:text-slate-100">{ocrConfidence}%</span>
          </span>
        )}
      </div>

      {/* Content Area */}
      <div className="p-4 sm:p-6">
        {activeTab === 'image' || activeTab === 'processed' ? (
          <div className="flex justify-center items-center bg-slate-950/5 dark:bg-slate-950/60 rounded-2xl p-4 min-h-[340px]">
            {loadingImg ? (
              <div className="flex flex-col items-center space-y-2 text-slate-500 dark:text-slate-400">
                <Loader2 className="h-8 w-8 animate-spin text-brand-600 dark:text-brand-400" />
                <span className="text-xs font-semibold">Loading packaging face {selectedFaceIdx + 1}...</span>
              </div>
            ) : currentDisplayUrl && !imgError ? (
              <img
                src={currentDisplayUrl}
                alt={activeTab === 'processed' ? `Enhanced Face ${selectedFaceIdx + 1}` : `Preserved Face ${selectedFaceIdx + 1}`}
                onError={() => setImgError(true)}
                className="max-h-[520px] w-auto object-contain rounded-xl shadow-sm border border-slate-200/80 dark:border-slate-700 bg-white dark:bg-slate-800"
              />
            ) : (
              <div className="text-slate-400 dark:text-slate-500 text-sm flex flex-col items-center space-y-2 py-8">
                <AlertCircle className="h-8 w-8 text-slate-400 dark:text-slate-500" />
                <span className="font-medium">Evidence image preview unavailable</span>
                <span className="text-xs text-slate-400 dark:text-slate-500">The uploaded file has been archived on disk.</span>
              </div>
            )}
          </div>
        ) : (
          <div className="bg-slate-900 dark:bg-slate-950 text-slate-100 p-5 rounded-2xl font-mono text-xs overflow-x-auto max-h-[520px] whitespace-pre-wrap leading-relaxed select-all border border-slate-800 dark:border-slate-800">
            {rawText || '// No text extracted by OCR engine.'}
          </div>
        )}
      </div>
    </div>
  );
};

export default EvidenceViewer;
