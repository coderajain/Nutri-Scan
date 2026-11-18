import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import apiClient from '../api/client';
import { ScoreCards } from '../components/ScoreCards';
import { EvidenceViewer } from '../components/EvidenceViewer';
import { FindingBadge, SeverityBadge } from '../components/StatusBadges';
import { Disclaimers } from '../components/Disclaimers';
import { Download, ArrowLeft, Clock, ShieldCheck, CheckCircle2, AlertTriangle, Eye, Table, Barcode, QrCode, ExternalLink } from 'lucide-react';

export const ScanResults = () => {
  const { id } = useParams();
  const [scan, setScan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('all'); // all, legal_metrology, nutrition, manual_review

  useEffect(() => {
    const fetchScanDetail = async () => {
      try {
        const res = await apiClient.get(`/scans/${id}`);
        setScan(res.data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to retrieve scan results.');
      } finally {
        setLoading(false);
      }
    };
    fetchScanDetail();
  }, [id]);

  const handleDownloadPDF = async () => {
    try {
      const response = await apiClient.get(`/scans/${id}/report`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `NutriScan_Audit_${id.substring(0, 8)}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (err) {
      alert('Failed to download PDF report.');
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center py-20">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-600"></div>
      </div>
    );
  }

  if (error || !scan) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        <div className="p-6 bg-red-50 text-red-700 rounded-2xl border border-red-200">
          <p className="font-bold">{error || 'Scan not found.'}</p>
          <Link to="/scan" className="mt-4 inline-block text-xs font-bold text-brand-600 underline">
            Start a new scan
          </Link>
        </div>
      </div>
    );
  }

  // Filter findings based on active tab
  const filteredFindings = (scan.findings || []).filter((f) => {
    if (activeTab === 'legal_metrology') return f.module === 'legal_metrology';
    if (activeTab === 'nutrition') return f.module === 'nutrition';
    if (activeTab === 'manual_review') return f.requires_manual_review || f.is_font_size_flag;
    return true;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
      {/* Top Breadcrumb & Actions */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-200 pb-4 mb-6">
        <Link
          to="/history"
          className="flex items-center space-x-1.5 text-xs font-bold text-slate-500 hover:text-slate-800 transition"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Scan History</span>
        </Link>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleDownloadPDF}
            className="flex items-center space-x-2 bg-metrology-600 hover:bg-metrology-700 text-white px-4 py-2 rounded-xl text-xs font-bold shadow-sm transition"
          >
            <Download className="h-4 w-4" />
            <span>Download Audit PDF (REP-004)</span>
          </button>
        </div>
      </div>

      {/* Product Title Banner */}
      <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-xs mb-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase bg-brand-100 text-brand-800">
                Packaged Commodity Audit
              </span>
              <span className="text-xs text-slate-400 font-mono">ID: {scan.id.substring(0, 8)}</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight mt-1">
              {scan.product_name || 'Packaged Commodity (Unlabeled)'}
            </h1>
            <p className="text-xs text-slate-500 mt-1 flex items-center space-x-2">
              <Clock className="h-3.5 w-3.5" />
              <span>Scanned on {new Date(scan.created_at).toLocaleString()}</span>
              <span>&bull;</span>
              <span>Rule Version: <b>{scan.rule_version_tag || 'LM-PC-2011-v1.0'}</b></span>
              {scan.scan_duration_ms && (
                <>
                  <span>&bull;</span>
                  <span>Pipeline Duration: {scan.scan_duration_ms}ms</span>
                </>
              )}
            </p>
          </div>
        </div>
      </div>

      {/* Independent Scores Cards (SCORE-001, SCORE-002) */}
      <ScoreCards
        complianceScore={scan.compliance_score}
        complianceStatus={scan.compliance_status}
        nutritionScore={scan.nutrition_score}
        nutritionStatus={scan.nutrition_status}
        isDataInsufficient={scan.is_data_insufficient}
        hasFontSizeFlags={scan.has_font_size_flags}
      />

      {/* Barcode & QR Code Section (SCAN-005, LM-004) */}
      <div className="my-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* 1D Barcode Card */}
        <div className="bg-white rounded-3xl p-5 border border-slate-200 shadow-xs flex items-start space-x-4">
          <div className={`p-3 rounded-2xl shrink-0 ${scan.barcode ? 'bg-indigo-50 text-indigo-600 border border-indigo-100' : 'bg-slate-50 text-slate-400'}`}>
            <Barcode className="h-6 w-6" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Packaging Barcode (GTIN)</h3>
              {scan.barcode && (
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-green-100 text-green-700">
                  Detected
                </span>
              )}
            </div>
            {scan.barcode ? (
              <div className="mt-1.5">
                <p className="text-xl font-mono font-black text-slate-900 tracking-wider">{scan.barcode}</p>
                <p className="text-xs text-slate-500 mt-1">
                  Format: <span className="font-semibold text-slate-700">{scan.barcode_format || 'EAN-13'}</span>
                  {scan.barcode_country && (
                    <> &bull; Origin: <span className="font-semibold text-indigo-700">{scan.barcode_country}</span></>
                  )}
                </p>
              </div>
            ) : (
              <p className="text-xs text-slate-400 italic mt-1.5">No 1D barcode detected on this packaging view</p>
            )}
          </div>
        </div>

        {/* 2D QR Code Card */}
        <div className="bg-white rounded-3xl p-5 border border-slate-200 shadow-xs flex items-start space-x-4">
          <div className={`p-3 rounded-2xl shrink-0 ${scan.qr_code ? 'bg-purple-50 text-purple-600 border border-purple-100' : 'bg-slate-50 text-slate-400'}`}>
            <QrCode className="h-6 w-6" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Smart QR Code</h3>
              {scan.qr_code && (
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-green-100 text-green-700">
                  Decoded
                </span>
              )}
            </div>
            {scan.qr_code ? (
              <div className="mt-1.5">
                <p className="text-xs font-mono text-slate-800 break-all bg-slate-50 p-2 rounded-xl border border-slate-200">
                  {scan.qr_code}
                </p>
                {scan.qr_code.startsWith('http') && (
                  <a
                    href={scan.qr_code}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center space-x-1 text-xs font-bold text-purple-600 hover:text-purple-800 mt-1.5 transition"
                  >
                    <span>Open Regulatory / Traceability Link</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                )}
              </div>
            ) : (
              <p className="text-xs text-slate-400 italic mt-1.5">No 2D QR code detected on this packaging view</p>
            )}
          </div>
        </div>
      </div>

      {/* Evidence Viewer (Original Image + Raw OCR Text) */}
      <div className="my-8">
        <h2 className="text-base font-extrabold text-slate-900 mb-3">Preserved Packaging Evidence (SCAN-003)</h2>
        <EvidenceViewer
          imageUrl={scan.original_image_url}
          processedImageUrl={scan.processed_image_url}
          evidenceImages={scan.evidence_images}
          rawText={scan.ocr_raw_text}
          ocrConfidence={scan.ocr_confidence_avg}
        />
      </div>

      {/* Extracted Structured Declarations Table */}
      <div className="my-8 bg-white rounded-3xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex justify-between items-center">
          <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
            <Table className="h-4 w-4 text-brand-600" />
            <span>Extracted Structured Declarations (OCR-005)</span>
          </h2>
          <span className="text-xs font-semibold text-slate-500">
            {scan.fields?.length || 0} fields identified
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-100 text-slate-700 uppercase tracking-wider text-[10px] font-extrabold">
              <tr>
                <th className="py-3 px-4">Declaration Field</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Normalized Value</th>
                <th className="py-3 px-4">Raw OCR Match</th>
                <th className="py-3 px-4">Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {scan.fields?.map((field) => (
                <tr key={field.id} className="hover:bg-slate-50">
                  <td className="py-3 px-4 font-bold text-slate-900">{field.field_name.replace(/_/g, ' ')}</td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded text-[10px] uppercase font-semibold bg-slate-100 text-slate-600">
                      {field.field_category}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-semibold text-brand-700">
                    {field.normalized_value || <span className="text-slate-400 font-normal">Not Declared</span>}
                  </td>
                  <td className="py-3 px-4 font-mono text-[11px] text-slate-600 truncate max-w-xs">
                    {field.raw_value || '—'}
                  </td>
                  <td className="py-3 px-4">
                    {field.confidence_score ? `${Math.round(field.confidence_score)}%` : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Detailed Regulatory & Nutritional Findings (LM-004) */}
      <div className="my-8 bg-white rounded-3xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-6 border-b border-slate-200 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h2 className="text-base font-extrabold text-slate-900">Granular Evaluation Findings (LM-004)</h2>
            <p className="text-xs text-slate-500 mt-0.5">Itemized statutory rules and nutritional assessment criteria</p>
          </div>

          {/* Filter Tabs */}
          <div className="flex bg-slate-100 p-1 rounded-xl text-xs font-bold text-slate-600">
            <button
              onClick={() => setActiveTab('all')}
              className={`px-3 py-1.5 rounded-lg transition ${activeTab === 'all' ? 'bg-white text-slate-900 shadow-xs' : ''}`}
            >
              All ({scan.findings?.length || 0})
            </button>
            <button
              onClick={() => setActiveTab('legal_metrology')}
              className={`px-3 py-1.5 rounded-lg transition ${activeTab === 'legal_metrology' ? 'bg-white text-slate-900 shadow-xs' : ''}`}
            >
              Legal Metrology
            </button>
            <button
              onClick={() => setActiveTab('nutrition')}
              className={`px-3 py-1.5 rounded-lg transition ${activeTab === 'nutrition' ? 'bg-white text-slate-900 shadow-xs' : ''}`}
            >
              Nutrition
            </button>
            <button
              onClick={() => setActiveTab('manual_review')}
              className={`px-3 py-1.5 rounded-lg transition ${activeTab === 'manual_review' ? 'bg-white text-slate-900 shadow-xs' : ''}`}
            >
              Manual Review
            </button>
          </div>
        </div>

        <div className="divide-y divide-slate-100">
          {filteredFindings.map((finding) => (
            <div key={finding.id} className="p-5 sm:px-6 hover:bg-slate-50 transition">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                <div className="flex items-center space-x-2">
                  <FindingBadge type={finding.finding_type} />
                  <SeverityBadge severity={finding.severity} />
                  <h4 className="text-sm font-bold text-slate-900">{finding.title}</h4>
                </div>
                <span className="text-[11px] font-mono text-slate-400 uppercase">
                  {finding.field_name}
                </span>
              </div>

              <p className="text-xs text-slate-600 mt-2 leading-relaxed">{finding.message}</p>

              <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-2 text-xs bg-slate-50 p-3 rounded-xl border border-slate-100">
                <div>
                  <span className="text-[10px] uppercase font-bold text-slate-400 block">Observed Evidence:</span>
                  <span className="font-semibold text-slate-800">{finding.observed_value || 'Not Found / Absent'}</span>
                </div>
                <div>
                  <span className="text-[10px] uppercase font-bold text-slate-400 block">Statutory / Clinical Condition:</span>
                  <span className="text-slate-600">{finding.expected_condition || '—'}</span>
                </div>
              </div>

              {finding.is_font_size_flag && (
                <div className="mt-2 text-[11px] text-amber-700 flex items-center space-x-1.5 font-medium">
                  <Eye className="h-3.5 w-3.5" />
                  <span>Flagged for Manual Verification: Digital image lacks physical millimeter calibration scale.</span>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Disclaimers (SAF-001, SAF-002) */}
      <Disclaimers />
    </div>
  );
};
export default ScanResults;
