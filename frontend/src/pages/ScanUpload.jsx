import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import apiClient from '../api/client';
import {
  UploadCloud,
  Camera,
  ArrowRight,
  AlertCircle,
  CheckCircle2,
  X,
  Layers,
  Sparkles,
  FileText,
  Package,
  ExternalLink,
  Plus
} from 'lucide-react';
import { Disclaimers } from '../components/Disclaimers';

export const ScanUpload = () => {
  const [files, setFiles] = useState([]);
  const [uploadMode, setUploadMode] = useState('multi_face'); // 'multi_face' or 'batch'
  const [productName, setProductName] = useState('');
  const [brandName, setBrandName] = useState('');
  const [ruleVersionTag, setRuleVersionTag] = useState('LM-PC-2011-v1.0');
  const [ruleVersions, setRuleVersions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [processingStage, setProcessingStage] = useState('');
  const [progressPct, setProgressPct] = useState(0);
  const [error, setError] = useState('');
  const [batchResults, setBatchResults] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Load available rule versions (LM-001)
    const fetchVersions = async () => {
      try {
        const res = await apiClient.get('/rules/versions');
        setRuleVersions(res.data);
      } catch (err) {
        console.error('Failed to load rule versions:', err);
      }
    };
    fetchVersions();
  }, []);

  const handleFilesAdded = (newFileList) => {
    if (!newFileList || newFileList.length === 0) return;

    const validTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp'];
    const maxBytes = 15 * 1024 * 1024;
    const addedFiles = [];
    let errMessage = '';

    Array.from(newFileList).forEach((file) => {
      if (!validTypes.includes(file.type)) {
        errMessage = `Skipped "${file.name}": Unsupported format. Allowed: JPG, PNG, WEBP.`;
        return;
      }
      if (file.size > maxBytes) {
        errMessage = `Skipped "${file.name}": Exceeds maximum 15MB limit.`;
        return;
      }
      addedFiles.push({
        file,
        preview: URL.createObjectURL(file),
        id: Math.random().toString(36).substring(2, 9),
      });
    });

    if (errMessage) {
      setError(errMessage);
    } else {
      setError('');
    }

    setFiles((prev) => [...prev, ...addedFiles]);
  };

  const handleRemoveFile = (idToRemove) => {
    setFiles((prev) => {
      const target = prev.find((item) => item.id === idToRemove);
      if (target && target.preview) {
        URL.revokeObjectURL(target.preview);
      }
      return prev.filter((item) => item.id !== idToRemove);
    });
  };

  const formatErrorMessage = (err, fallback) => {
    const detail = err.response?.data?.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
      return detail.map((d) => (typeof d === 'object' ? d.msg || JSON.stringify(d) : String(d))).join('; ');
    }
    if (detail && typeof detail === 'object') {
      return detail.message || JSON.stringify(detail);
    }
    return err.message || fallback;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (files.length === 0) {
      setError('Please select or capture at least one packaging image.');
      return;
    }

    setError('');
    setLoading(true);
    setBatchResults(null);

    const formData = new FormData();
    // Append primary face as 'file' for maximum compatibility with all backend versions
    if (files.length > 0) {
      formData.append('file', files[0].file);
    }
    // Append all faces as 'files' for multi-view processing
    if (files.length > 1 || uploadMode === 'batch') {
      files.forEach((item) => {
        formData.append('files', item.file);
      });
    }
    formData.append('rule_version_tag', ruleVersionTag);

    if (uploadMode === 'multi_face') {
      if (productName) formData.append('product_name', productName);
      if (brandName) formData.append('brand_name', brandName);

      setProcessingStage(`1/4: Enhancing ${files.length} packaging view${files.length > 1 ? 's' : ''} with OpenCV & CLAHE...`);
      setProgressPct(25);

      const timer1 = setTimeout(() => {
        setProcessingStage('2/4: Scanning 1D/2D Barcodes, GS1 prefixes & QR codes...');
        setProgressPct(50);
      }, 700);

      const timer2 = setTimeout(() => {
        setProcessingStage('3/4: High-speed OCR text recognition & field extraction...');
        setProgressPct(75);
      }, 1500);

      const timer3 = setTimeout(() => {
        setProcessingStage('4/4: Evaluating Legal Metrology rules & generating audit PDF...');
        setProgressPct(90);
      }, 2500);

      const timer4 = setTimeout(() => {
        setProcessingStage('Compiling final compliance report...');
        setProgressPct(95);
      }, 4000);

      try {
        const res = await apiClient.post('/scans/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        clearTimeout(timer1);
        clearTimeout(timer2);
        clearTimeout(timer3);
        clearTimeout(timer4);
        setProgressPct(100);
        setProcessingStage('Analysis complete! Redirecting to audit report...');
        navigate(`/scan/${res.data.id}`);
      } catch (err) {
        clearTimeout(timer1);
        clearTimeout(timer2);
        clearTimeout(timer3);
        clearTimeout(timer4);
        setError(formatErrorMessage(err, 'Multi-view scan failed. Please check image quality.'));
        setLoading(false);
      }
    } else {
      // Batch mode
      setProcessingStage(`Batch auditing ${files.length} individual packaged products...`);
      setProgressPct(50);
      try {
        const res = await apiClient.post('/scans/batch', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        setProgressPct(100);
        setBatchResults(res.data);
        setLoading(false);
      } catch (err) {
        setError(formatErrorMessage(err, 'Batch processing failed.'));
        setLoading(false);
      }
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
      {/* Title */}
      <div className="text-center mb-8">
        <span className="text-xs font-bold text-brand-600 dark:text-brand-400 uppercase tracking-wider">Packaged Commodity Audit</span>
        <h1 className="text-3xl font-black text-slate-900 dark:text-slate-100 tracking-tight mt-1">
          Scan & Analyze Packaging
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 max-w-xl mx-auto">
          Upload single or multiple packaging faces (Front, Back, Nutrition Facts Table, Barcode) for a unified regulatory & nutritional compliance audit.
        </p>
      </div>

      {/* Mode Selector */}
      <div className="flex justify-center mb-6">
        <div className="bg-slate-100 dark:bg-slate-800/80 p-1 rounded-2xl flex space-x-1 border border-slate-200 dark:border-slate-700">
          <button
            type="button"
            onClick={() => { setUploadMode('multi_face'); setBatchResults(null); }}
            className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold transition ${
              uploadMode === 'multi_face'
                ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <Layers className="h-4 w-4 text-brand-600 dark:text-brand-400" />
            <span>Multi-Face Package Scan</span>
            <span className="text-[10px] bg-brand-50 dark:bg-emerald-950/60 text-brand-700 dark:text-brand-300 px-1.5 py-0.5 rounded-md font-semibold">Single Item</span>
          </button>
          <button
            type="button"
            onClick={() => { setUploadMode('batch'); setBatchResults(null); }}
            className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold transition ${
              uploadMode === 'batch'
                ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <Package className="h-4 w-4 text-metrology-600 dark:text-metrology-400" />
            <span>Batch Product Scan</span>
            <span className="text-[10px] bg-slate-200 dark:bg-slate-600 text-slate-700 dark:text-slate-200 px-1.5 py-0.5 rounded-md font-semibold">Multiple Items</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-2xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900/60 text-red-700 dark:text-red-300 text-xs flex items-center space-x-2">
          <AlertCircle className="h-5 w-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Batch Results View (if completed) */}
      {batchResults && (
        <div className="mb-8 bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-xs transition-colors">
          <div className="flex items-center justify-between pb-4 border-b border-slate-200 dark:border-slate-800 mb-4">
            <h2 className="text-base font-extrabold text-slate-900 dark:text-slate-100 flex items-center space-x-2">
              <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />
              <span>Batch Audit Completed ({batchResults.successful_scans.length} / {batchResults.total_uploaded} Scanned)</span>
            </h2>
            <button
              onClick={() => { setBatchResults(null); setFiles([]); }}
              className="text-xs font-bold text-brand-600 dark:text-brand-400 hover:underline"
            >
              Start New Upload
            </button>
          </div>

          <div className="space-y-3">
            {batchResults.successful_scans.map((item, idx) => (
              <div
                key={item.id}
                className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
              >
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-bold text-slate-400 dark:text-slate-500">#{idx + 1}</span>
                    <span className="text-sm font-bold text-slate-900 dark:text-slate-100">{item.product_name || 'Packaged Commodity'}</span>
                    {item.barcode && (
                      <span className="text-[10px] font-mono bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 px-2 py-0.5 rounded-full font-bold">
                        {item.barcode}
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-slate-500 dark:text-slate-400 mt-1 flex items-center space-x-3">
                    <span>Legal Metrology: <b>{item.compliance_score !== null ? `${Math.round(item.compliance_score)}/100` : '—'}</b></span>
                    <span>&bull;</span>
                    <span>Nutrition: <b>{item.nutrition_score !== null ? `${Math.round(item.nutrition_score)}/100` : 'Insufficient'}</b></span>
                  </div>
                </div>

                <Link
                  to={`/scan/${item.id}`}
                  className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-xs font-bold transition shrink-0"
                >
                  <span>View Audit</span>
                  <ExternalLink className="h-3.5 w-3.5" />
                </Link>
              </div>
            ))}
          </div>
        </div>
      )}

      {loading ? (
        <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 p-12 text-center shadow-xs transition-colors">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-brand-500 border-t-transparent mx-auto"></div>
          <h3 className="mt-6 text-lg font-bold text-slate-900 dark:text-slate-100">
            {uploadMode === 'multi_face' ? 'Processing Multi-View Package Audit' : 'Executing Batch Product Analysis'}
          </h3>
          <p className="mt-2 text-xs font-medium text-slate-600 dark:text-slate-400 animate-pulse">{processingStage}</p>
          <div className="mt-6 max-w-sm mx-auto">
            <div className="bg-slate-100 dark:bg-slate-800 rounded-full h-2.5 overflow-hidden">
              <div
                className="bg-brand-600 h-full transition-all duration-500 ease-out rounded-full"
                style={{ width: `${progressPct}%` }}
              ></div>
            </div>
            <div className="flex justify-between items-center mt-2 text-[10px] text-slate-400 font-semibold px-1">
              <span>Auditing</span>
              <span>{progressPct}%</span>
            </div>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Multi-File Upload Drop Area */}
          <div className="bg-white dark:bg-slate-900 rounded-3xl border-2 border-dashed border-slate-300 dark:border-slate-700 p-6 sm:p-8 hover:border-brand-500 dark:hover:border-brand-500 transition relative text-center">
            <input
              type="file"
              multiple
              accept="image/jpeg,image/png,image/jpg,image/webp"
              onChange={(e) => handleFilesAdded(e.target.files)}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
            />
            <div className="flex flex-col items-center">
              <div className="p-4 bg-brand-50 dark:bg-emerald-950/60 rounded-2xl text-brand-600 dark:text-brand-400 mb-3">
                <UploadCloud className="h-8 w-8" />
              </div>
              <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                {uploadMode === 'multi_face'
                  ? 'Drop or Select Multiple Package Faces'
                  : 'Drop Multiple Product Images for Batch Audit'}
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                {uploadMode === 'multi_face'
                  ? 'Select 1 or more photos: Front (PDP), Back (Nutrition Table & Ingredients), Barcode / Side face'
                  : 'Upload up to 15 different product label images simultaneously'}
              </p>
              <div className="mt-4 flex items-center space-x-2 text-xs text-slate-400 dark:text-slate-500">
                <Camera className="h-4 w-4" />
                <span>Supports multiple photo selections (JPG, PNG, WEBP up to 15MB each)</span>
              </div>
            </div>
          </div>

          {/* Selected Files Thumbnail Preview Grid */}
          {files.length > 0 && (
            <div className="bg-white dark:bg-slate-900 p-5 rounded-3xl border border-slate-200 dark:border-slate-800 transition-colors">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800 mb-3">
                <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                  Selected Images ({files.length})
                </h3>
                <span className="text-[11px] text-brand-600 dark:text-brand-400 font-semibold">
                  {uploadMode === 'multi_face'
                    ? 'All faces will be merged into one unified audit'
                    : 'Each image will generate a separate product audit'}
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                {files.map((item, idx) => (
                  <div
                    key={item.id}
                    className="relative group rounded-2xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/80 p-2 flex flex-col items-center text-center overflow-hidden"
                  >
                    <button
                      type="button"
                      onClick={() => handleRemoveFile(item.id)}
                      className="absolute top-2 right-2 bg-red-600 text-white rounded-full p-1 shadow-md hover:bg-red-700 transition z-20"
                      title="Remove image"
                    >
                      <X className="h-3 w-3" />
                    </button>
                    <img
                      src={item.preview}
                      alt={`Upload preview ${idx + 1}`}
                      className="h-24 w-full object-contain rounded-xl bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800"
                    />
                    <div className="mt-2 w-full px-1">
                      <span className="text-[10px] font-bold text-slate-700 dark:text-slate-200 block truncate">
                        {uploadMode === 'multi_face' ? `Face ${idx + 1}: ${item.file.name}` : item.file.name}
                      </span>
                      <span className="text-[9px] text-slate-400 dark:text-slate-500">
                        {(item.file.size / (1024 * 1024)).toFixed(2)} MB
                      </span>
                    </div>
                  </div>
                ))}

                {/* Add more files card */}
                <label className="border-2 border-dashed border-slate-200 dark:border-slate-700 hover:border-brand-400 dark:hover:border-brand-500 rounded-2xl flex flex-col items-center justify-center p-4 cursor-pointer text-slate-400 dark:text-slate-500 hover:text-brand-600 dark:hover:text-brand-400 transition min-h-[120px]">
                  <input
                    type="file"
                    multiple
                    accept="image/jpeg,image/png,image/jpg,image/webp"
                    onChange={(e) => handleFilesAdded(e.target.files)}
                    className="hidden"
                  />
                  <Plus className="h-6 w-6 mb-1" />
                  <span className="text-[11px] font-bold">Add Another Face</span>
                </label>
              </div>
            </div>
          )}

          {/* Optional Metadata (for multi-face single item) & Version Selection */}
          <div className="bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-200 dark:border-slate-800 grid grid-cols-1 md:grid-cols-3 gap-4 transition-colors">
            {uploadMode === 'multi_face' && (
              <>
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                    Product Name (Optional)
                  </label>
                  <input
                    type="text"
                    value={productName}
                    onChange={(e) => setProductName(e.target.value)}
                    placeholder="e.g. Malai Paneer"
                    className="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 focus:ring-2 focus:ring-brand-500 focus:outline-none focus:bg-white dark:focus:bg-slate-800"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                    Brand Name (Optional)
                  </label>
                  <input
                    type="text"
                    value={brandName}
                    onChange={(e) => setBrandName(e.target.value)}
                    placeholder="e.g. Amul"
                    className="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 focus:ring-2 focus:ring-brand-500 focus:outline-none focus:bg-white dark:focus:bg-slate-800"
                  />
                </div>
              </>
            )}

            <div className={uploadMode === 'batch' ? 'md:col-span-3' : ''}>
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1 flex items-center justify-between">
                <span>Statutory Rule Version</span>
                <span className="text-[10px] text-metrology-600 dark:text-metrology-400 font-semibold">LM-001</span>
              </label>
              <select
                value={ruleVersionTag}
                onChange={(e) => setRuleVersionTag(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-semibold focus:ring-2 focus:ring-brand-500 focus:outline-none focus:bg-white dark:focus:bg-slate-800 text-slate-800 dark:text-slate-200"
              >
                {ruleVersions.map((v) => (
                  <option key={v.id} value={v.version_tag}>
                    {v.version_tag} {v.is_active ? '(Active Standard)' : ''}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={files.length === 0 || loading}
            className="w-full bg-brand-600 hover:bg-brand-700 text-white font-extrabold py-3.5 rounded-2xl shadow-sm text-sm flex items-center justify-center space-x-2 transition disabled:opacity-50"
          >
            <span>
              {uploadMode === 'multi_face'
                ? `Analyze ${files.length > 0 ? `${files.length} Packaging Face${files.length > 1 ? 's' : ''}` : 'Packaging'} & Verify Compliance`
                : `Execute Batch Audit (${files.length} Product${files.length !== 1 ? 's' : ''})`}
            </span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </form>
      )}

      {/* SRS Disclaimers */}
      <Disclaimers />
    </div>
  );
};

export default ScanUpload;
