import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/client';
import { UploadCloud, Camera, ArrowRight, AlertCircle, CheckCircle2, ShieldCheck, Scale } from 'lucide-react';
import { Disclaimers } from '../components/Disclaimers';

export const ScanUpload = () => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [productName, setProductName] = useState('');
  const [brandName, setBrandName] = useState('');
  const [ruleVersionTag, setRuleVersionTag] = useState('LM-PC-2011-v1.0');
  const [ruleVersions, setRuleVersions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [processingStage, setProcessingStage] = useState('');
  const [error, setError] = useState('');
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

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (!selected) return;

    // Validate size (<= 15MB) (SCAN-002, NFR-PERF-007)
    if (selected.size > 15 * 1024 * 1024) {
      setError('File exceeds maximum upload size of 15MB.');
      return;
    }

    // Validate type (SCAN-001)
    const validTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp'];
    if (!validTypes.includes(selected.type)) {
      setError('Unsupported file format. Please upload JPG, JPEG, PNG, or WEBP.');
      return;
    }

    setError('');
    setFile(selected);
    setPreview(URL.createObjectURL(selected));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select or capture a label image.');
      return;
    }

    setError('');
    setLoading(true);

    // Processing animation stages (NFR-PERF-003)
    setProcessingStage('1/5: Preserving evidence and executing OpenCV preprocessing...');
    const stageTimer1 = setTimeout(() => {
      setProcessingStage('2/5: Invoking Tesseract OCR text recognition engine...');
    }, 1500);
    const stageTimer2 = setTimeout(() => {
      setProcessingStage('3/5: Extracting packaged commodity declarations & nutrition table...');
    }, 3500);
    const stageTimer3 = setTimeout(() => {
      setProcessingStage('4/5: Evaluating Legal Metrology statutory rules & ICMR criteria...');
    }, 5500);
    const stageTimer4 = setTimeout(() => {
      setProcessingStage('5/5: Generating publication-grade ReportLab PDF report...');
    }, 7500);

    const formData = new FormData();
    formData.append('file', file);
    if (productName) formData.append('product_name', productName);
    if (brandName) formData.append('brand_name', brandName);
    formData.append('rule_version_tag', ruleVersionTag);

    try {
      const res = await apiClient.post('/scans/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      clearTimeout(stageTimer1);
      clearTimeout(stageTimer2);
      clearTimeout(stageTimer3);
      clearTimeout(stageTimer4);
      navigate(`/scan/${res.data.id}`);
    } catch (err) {
      clearTimeout(stageTimer1);
      clearTimeout(stageTimer2);
      clearTimeout(stageTimer3);
      clearTimeout(stageTimer4);
      setError(err.response?.data?.detail || 'Scan processing failed. Please ensure the image is clear.');
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
      <div className="text-center mb-8">
        <span className="text-xs font-bold text-brand-600 uppercase tracking-wider">Packaged Commodity Scanner</span>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-1">
          Scan & Analyze Label Image
        </h1>
        <p className="text-sm text-slate-500 mt-1 max-w-xl mx-auto">
          Upload or capture a clear photo of the food packaging label. NutriScan extracts visible text, verifies statutory declarations, and calculates compliance and nutrition scores.
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-2xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center space-x-2">
          <AlertCircle className="h-5 w-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="bg-white rounded-3xl border border-slate-200 p-12 text-center shadow-xs">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-brand-500 border-t-transparent mx-auto"></div>
          <h3 className="mt-6 text-lg font-bold text-slate-900">Processing Packaged Commodity Label</h3>
          <p className="mt-2 text-xs font-medium text-slate-500 animate-pulse">{processingStage}</p>
          <div className="mt-6 max-w-xs mx-auto bg-slate-100 rounded-full h-2 overflow-hidden">
            <div className="bg-brand-600 h-full w-2/3 animate-pulse"></div>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Upload Area */}
          <div className="bg-white rounded-3xl border-2 border-dashed border-slate-300 p-8 hover:border-brand-500 transition cursor-pointer relative text-center">
            <input
              type="file"
              accept="image/jpeg,image/png,image/jpg,image/webp"
              onChange={handleFileChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            {preview ? (
              <div className="flex flex-col items-center">
                <img
                  src={preview}
                  alt="Label Preview"
                  className="max-h-72 rounded-2xl shadow-sm border border-slate-200 object-contain"
                />
                <p className="mt-4 text-xs font-bold text-brand-600">Click or tap to replace photo</p>
              </div>
            ) : (
              <div className="py-8 flex flex-col items-center">
                <div className="p-4 bg-brand-50 rounded-2xl text-brand-600 mb-3">
                  <UploadCloud className="h-8 w-8" />
                </div>
                <h3 className="text-base font-bold text-slate-900">Upload Label Photograph</h3>
                <p className="text-xs text-slate-500 mt-1">PNG, JPG, or WEBP up to 15MB</p>
                <div className="mt-4 flex items-center space-x-2 text-xs text-slate-400">
                  <Camera className="h-4 w-4" />
                  <span>Supports desktop file browser or smartphone camera capture</span>
                </div>
              </div>
            )}
          </div>

          {/* Optional Metadata & Version Selection */}
          <div className="bg-white p-6 rounded-3xl border border-slate-200 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Product Name (Optional)
              </label>
              <input
                type="text"
                value={productName}
                onChange={(e) => setProductName(e.target.value)}
                placeholder="e.g. Whole Wheat Biscuits"
                className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-brand-500 focus:outline-none focus:bg-white"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Brand Name (Optional)
              </label>
              <input
                type="text"
                value={brandName}
                onChange={(e) => setBrandName(e.target.value)}
                placeholder="e.g. Healthy Harvest"
                className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-brand-500 focus:outline-none focus:bg-white"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1 flex items-center justify-between">
                <span>Statutory Rule Version</span>
                <span className="text-[10px] text-metrology-600 font-semibold">LM-001</span>
              </label>
              <select
                value={ruleVersionTag}
                onChange={(e) => setRuleVersionTag(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold focus:ring-2 focus:ring-brand-500 focus:outline-none focus:bg-white text-slate-800"
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
            disabled={!file || loading}
            className="w-full bg-brand-600 hover:bg-brand-700 text-white font-extrabold py-3.5 rounded-2xl shadow-sm text-sm flex items-center justify-center space-x-2 transition disabled:opacity-50"
          >
            <span>Analyze & Verify Compliance</span>
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
