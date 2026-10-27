'use client';

import React from "react"
import { useState, useEffect } from 'react';
import {
  Upload,
  CheckCircle,
  FileText,
  Loader2,
  X,
  AlertCircle,
  ArrowRight,
  ShieldCheck,
  FileSearch,
  ClipboardList,
  CheckCircle2,
  AlertTriangle,
  ExternalLink,
  ChevronRight
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { Progress } from "@/components/ui/progress";

interface UploadedFile {
  id: string;
  file: File;
  progress: number;
  status: 'uploading' | 'completed' | 'error';
  errorMessage?: string;
}

// Re-defining Search since it might be missing from lucide
const Search = FileSearch;

const AUDIT_STEPS = [
  { id: 'upload', label: 'Upload Documents', icon: Upload },
  { id: 'rules', label: 'Compliance Standards', icon: ShieldCheck },
  { id: 'plan', label: 'Audit Strategy', icon: ClipboardList },
  { id: 'ocr', label: 'OCR Extraction', icon: FileSearch },
  { id: 'analysis', label: 'Gap Analysis', icon: Search },
  { id: 'approval', label: 'Human Verification', icon: CheckCircle2 },
  { id: 'report', label: 'Audit Report', icon: FileText },
];

export default function DocumentUpload() {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [interruptData, setInterruptData] = useState<any>(null);
  const [auditReport, setAuditReport] = useState<string | null>(null);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [auditState, setAuditState] = useState<'idle' | 'uploading' | 'processing' | 'interrupted' | 'completed'>('idle');

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const processFiles = (newFiles: File[]) => {
    const validFiles = newFiles.filter((file) => {
      const isValidType = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel',
        'image/jpeg',
        'image/png',
        'image/webp'
      ].includes(file.type);

      if (!isValidType) {
        toast.error(`File type not supported: ${file.name}`);
      }
      return isValidType;
    });

    const newUploadedFiles: UploadedFile[] = validFiles.map((file) => ({
      id: Math.random().toString(36).substring(2, 11),
      file,
      progress: 100,
      status: 'completed',
    }));

    setFiles((prev) => [...prev, ...newUploadedFiles]);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFiles = Array.from(e.dataTransfer.files);
    processFiles(droppedFiles);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    processFiles(selectedFiles);
    e.target.value = '';
  };

  const uploadFiles = async () => {
    if (files.length === 0) return;

    setIsAnalyzing(true);
    setAuditState('processing');
    setCurrentStepIndex(1); // Moving to Rules
    setInterruptData(null);
    setAuditReport(null);

    // Simulate progress through phases for better UX
    const simulateProgress = async () => {
      await new Promise(r => setTimeout(r, 1500));
      setCurrentStepIndex(2); // Plan
      await new Promise(r => setTimeout(r, 1500));
      setCurrentStepIndex(3); // OCR
    };

    simulateProgress();

    try {
      const formData = new FormData();
      files.forEach((fileObj) => {
        formData.append('file', fileObj.file);
      });

      const response = await fetch("http://127.0.0.1:4000/ocr", {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('OCR Response:', data);

      if (data.__interrupt__) {
        setCurrentStepIndex(5); // Approval
        setInterruptData(data.__interrupt__[0]);
        setAuditState('interrupted');
        toast.info('Compliance check complete: Action required');
      } else if (data.audit_report) {
        setCurrentStepIndex(6); // Report
        setAuditReport(data.audit_report);
        setAuditState('completed');
        toast.success('Audit successfully finalized');
      } else {
        setAuditState('completed');
        toast.success('Documents processed');
      }

    } catch (error) {
      console.error('Error uploading files:', error);
      toast.error('Failed to process documents');
      setAuditState('idle');
      setCurrentStepIndex(0);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleResume = async (approval: string) => {
    setIsAnalyzing(true);
    setAuditState('processing');
    setCurrentStepIndex(5); // Approval phase (processing resume)

    try {
      const response = await fetch("http://127.0.0.1:4000/resume", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          thread_id: "1",
          approval: approval
        })
      });

      if (!response.ok) {
        throw new Error(`Resume failed: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Resume Response:', data);

      if (data.audit_report) {
        setCurrentStepIndex(6); // Report
        setAuditReport(data.audit_report);
        setInterruptData(null);
        setAuditState('completed');
        toast.success('Audit report generated successfully');
      } else if (data.interrupt) {
        setInterruptData(data.interrupt[0]);
        setAuditState('interrupted');
      } else if (approval === 'No' || String(approval).toLowerCase() === 'no') {
        setInterruptData(null);
        setAuditState('idle');
        setCurrentStepIndex(0);
        toast.info('Audit workflow cancelled by user');
      } else {
        setInterruptData(null);
        setAuditState('completed');
        toast.info('Workflow finished');
      }
    } catch (error) {
      console.error('Error resuming workflow:', error);
      toast.error('Failed to resume audit');
      setAuditState('interrupted');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <section id="upload" className="relative py-24 px-4 sm:px-6 lg:px-8 overflow-hidden">
      {/* Dynamic Background Elements */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-primary/5 rounded-full filter blur-[100px] opacity-40 animate-pulse"></div>
        <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-accent/5 rounded-full filter blur-[100px] opacity-40 animate-pulse" style={{ animationDelay: '2s' }}></div>
      </div>

      <div className="relative z-10 max-w-5xl mx-auto">
        {/* Progress Stepper */}
        {(auditState !== 'idle' || files.length > 0) && (
          <div className="mb-16 px-4">
            <div className="relative flex justify-between items-center max-w-3xl mx-auto">
              {/* Progress Line */}
              <div className="absolute top-1/2 left-0 w-full h-0.5 bg-muted -translate-y-1/2 z-0">
                <div
                  className="h-full bg-gradient-to-r from-primary to-accent transition-all duration-1000 ease-in-out"
                  style={{ width: `${(currentStepIndex / (AUDIT_STEPS.length - 1)) * 100}%` }}
                ></div>
              </div>

              {AUDIT_STEPS.map((step, index) => {
                const Icon = step.icon;
                const isActive = index <= currentStepIndex;
                const isCurrent = index === currentStepIndex;

                return (
                  <div key={step.id} className="relative z-10 flex flex-col items-center">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center transition-all duration-500 border-2 ${isActive
                        ? 'bg-background border-primary text-primary shadow-lg shadow-primary/20 scale-110'
                        : 'bg-muted border-muted text-muted-foreground'
                      } ${isCurrent ? 'animate-bounce-subtle ring-4 ring-primary/10' : ''}`}>
                      {isActive && index < currentStepIndex ? (
                        <CheckCircle2 className="w-6 h-6" />
                      ) : (
                        <Icon className="w-5 h-5" />
                      )}
                    </div>
                    <span className={`absolute -bottom-8 text-[10px] font-bold uppercase tracking-wider whitespace-nowrap transition-colors duration-500 ${isActive ? 'text-foreground' : 'text-muted-foreground/50'
                      }`}>
                      {step.label}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {auditState === 'idle' && files.length === 0 && (
          <div className="text-center mb-12 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <h2 className="text-4xl sm:text-5xl font-extrabold text-foreground mb-6 tracking-tight">
              Audit <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">Engine v2.0</span>
            </h2>
            <p className="text-xl text-foreground/60 max-w-2xl mx-auto leading-relaxed">
              Upload compliance documents for instant AI-driven gap analysis and automated regulatory reporting.
            </p>
          </div>
        )}

        {/* Action Panel */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: Upload & File List */}
          <div className={`${auditState === 'idle' && files.length === 0 ? 'lg:col-span-12' : 'lg:col-span-5'} transition-all duration-700`}>
            {auditState === 'idle' && files.length === 0 ? (
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`group relative border-2 border-dashed rounded-3xl p-12 sm:p-20 text-center transition-all duration-500 bg-card/40 backdrop-blur-xl ${isDragging ? 'border-primary ring-4 ring-primary/10 bg-primary/5' : 'border-border/60 hover:border-primary/40'
                  }`}
              >
                <div className="flex flex-col items-center gap-6">
                  <div className={`w-24 h-24 rounded-2xl flex items-center justify-center transition-all duration-500 ${isDragging ? 'bg-primary text-white rotate-12 scale-110' : 'bg-primary/10 text-primary group-hover:bg-primary/20'
                    }`}>
                    <Upload className="w-10 h-10" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-foreground mb-3 leading-tight">
                      {isDragging ? 'Ready to Analysis' : 'Drop compliance files'}
                    </h3>
                    <p className="text-lg text-foreground/50 max-w-xs mx-auto mb-8 leading-relaxed">
                      Drag and drop your PDF, DOCX or Image files to begin the audit.
                    </p>
                  </div>
                  <label className="cursor-pointer group/btn">
                    <div className="px-8 py-4 bg-foreground text-background font-bold rounded-2xl hover:bg-primary hover:text-white transition-all duration-300 shadow-xl shadow-black/5 flex items-center gap-3">
                      Browse Files
                      <ArrowRight className="w-5 h-5 group-hover/btn:translate-x-1 transition-transform" />
                    </div>
                    <input type="file" multiple onChange={handleFileSelect} className="hidden" />
                  </label>
                </div>
              </div>
            ) : (
              <div className="bg-card/40 backdrop-blur-xl border border-border/60 rounded-3xl p-6 shadow-xl animate-in fade-in slide-in-from-left-4 duration-500">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-bold flex items-center gap-2">
                    <FileText className="w-5 h-5 text-primary" />
                    Documents
                  </h3>
                  <span className="bg-muted px-3 py-1 rounded-full text-xs font-bold text-muted-foreground uppercase tracking-widest">
                    {files.length} Files
                  </span>
                </div>

                <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                  {files.map((file) => (
                    <div key={file.id} className="group relative bg-muted/30 border border-transparent hover:border-primary/20 rounded-2xl p-4 transition-all overflow-hidden">
                      <div className="flex items-center gap-4 relative z-10">
                        <div className="w-10 h-10 rounded-xl bg-background flex items-center justify-center flex-shrink-0 shadow-sm">
                          <FileText className="w-5 h-5 text-primary/60" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-bold truncate pr-6">{file.file.name}</p>
                          <p className="text-xs text-muted-foreground font-medium">{formatFileSize(file.file.size)}</p>
                        </div>
                        {auditState === 'idle' && (
                          <button
                            onClick={() => removeFile(file.id)}
                            className="p-1.5 bg-background border border-border rounded-lg text-muted-foreground hover:text-destructive hover:border-destructive/30 transition-all opacity-0 group-hover:opacity-100"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                      <div className="absolute bottom-0 left-0 h-1 bg-primary/20 w-full">
                        <div className="h-full bg-primary transition-all duration-500" style={{ width: `${file.progress}%` }}></div>
                      </div>
                    </div>
                  ))}
                </div>

                {auditState === 'idle' && files.length > 0 && (
                  <Button
                    onClick={uploadFiles}
                    className="w-full mt-8 bg-primary hover:bg-primary/90 text-white h-14 rounded-2xl font-bold text-lg shadow-xl shadow-primary/20 transition-all active:scale-95 group"
                    disabled={isAnalyzing}
                  >
                    {isAnalyzing ? (
                      <div className="flex items-center gap-3">
                        <Loader2 className="w-6 h-6 animate-spin" />
                        <span>Initializing AI...</span>
                      </div>
                    ) : (
                      <div className="flex items-center gap-3">
                        <span>Execute Audit System</span>
                        <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                      </div>
                    )}
                  </Button>
                )}

                {auditState === 'idle' && files.length > 0 && (
                  <div className="mt-4">
                    <label className="cursor-pointer text-xs font-bold text-primary hover:underline flex items-center justify-center gap-1">
                      Add more files
                      <input type="file" multiple onChange={handleFileSelect} className="hidden" />
                    </label>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Right Column: Dynamic Status/Results */}
          {auditState !== 'idle' && (
            <div className="lg:col-span-7 space-y-8 animate-in fade-in slide-in-from-right-4 duration-700">
              {/* Processing Placeholder */}
              {isAnalyzing && !interruptData && !auditReport && (
                <div className="bg-card/40 backdrop-blur-xl border border-border/60 rounded-3xl p-10 flex flex-col items-center justify-center text-center min-h-[400px]">
                  <div className="relative mb-8">
                    <div className="w-24 h-24 rounded-full border-4 border-primary/20 border-t-primary animate-spin"></div>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <ShieldCheck className="w-8 h-8 text-primary animate-pulse" />
                    </div>
                  </div>
                  <h3 className="text-2xl font-bold mb-4">Processing Compliance</h3>
                  <div className="space-y-4 w-full max-w-sm">
                    <div className="flex justify-between text-xs font-bold uppercase tracking-tighter text-muted-foreground px-1">
                      <span>Analyzing Metadata</span>
                      <span>{currentStepIndex * 15}%</span>
                    </div>
                    <Progress value={currentStepIndex * 15} className="h-2" />
                    <p className="text-sm text-foreground/40 italic">"Leveraging deep learning for structural validation..."</p>
                  </div>
                </div>
              )}

              {/* Approval Interrupt UI */}
              {auditState === 'interrupted' && interruptData && (
                <div className="bg-amber-500/5 backdrop-blur-xl border-2 border-amber-500/20 rounded-3xl p-8 sm:p-10 shadow-2xl shadow-amber-500/5 relative overflow-hidden group">
                  <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:scale-125 transition-transform duration-700">
                    <AlertTriangle className="w-24 h-24 text-amber-500" />
                  </div>

                  <div className="relative z-10">
                    <div className="flex items-center gap-4 mb-8">
                      <div className="w-14 h-14 rounded-2xl bg-amber-500 flex items-center justify-center shadow-lg shadow-amber-500/20">
                        <AlertTriangle className="w-8 h-8 text-white" />
                      </div>
                      <div>
                        <h3 className="text-2xl font-black text-amber-600 dark:text-amber-500 tracking-tight">Compliance Alert</h3>
                        <p className="text-amber-700/60 dark:text-amber-400/60 font-medium">Critical Gaps Identified</p>
                      </div>
                    </div>

                    <div className="bg-white/40 dark:bg-black/20 rounded-2xl p-6 mb-10 border border-amber-500/10">
                      <h4 className="text-sm font-bold text-amber-700/80 dark:text-amber-400/80 uppercase tracking-widest mb-6 flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></div>
                        Missing Audit Sections
                      </h4>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {interruptData.value.missing_sections.map((section: string, index: number) => (
                          <div key={index} className="flex items-center gap-3 bg-amber-500/5 p-3 rounded-xl border border-amber-500/10 hover:bg-amber-500/10 transition-all">
                            <span className="w-6 h-6 rounded-lg bg-amber-500/20 text-amber-600 flex items-center justify-center text-xs font-black">{index + 1}</span>
                            <span className="text-sm font-semibold text-foreground/80">{section}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="flex flex-col sm:flex-row gap-4">
                      <Button
                        onClick={() => handleResume('Yes')}
                        className="flex-1 bg-amber-600 hover:bg-amber-700 text-white font-black h-16 rounded-2xl text-lg shadow-xl shadow-amber-500/20 active:scale-95 transition-all"
                        disabled={isAnalyzing}
                      >
                        {isAnalyzing ? (
                          <Loader2 className="mr-2 h-6 w-6 animate-spin" />
                        ) : (
                          'Override & Continue'
                        )}
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => handleResume('No')}
                        className="flex-1 border-2 border-amber-500/30 text-amber-700 dark:text-amber-500 hover:bg-amber-500/10 font-black h-16 rounded-2xl text-lg active:scale-95 transition-all"
                        disabled={isAnalyzing}
                      >
                        Abort Protocol
                      </Button>
                    </div>

                    <p className="mt-6 text-center text-xs font-bold text-amber-700/40 uppercase tracking-tighter">
                      Human verification required to proceed with incomplete data set
                    </p>
                  </div>
                </div>
              )}

              {/* Final Audit Report UI */}
              {auditState === 'completed' && auditReport && (
                <div className="bg-primary/5 backdrop-blur-3xl border border-primary/20 rounded-3xl p-8 sm:p-10 shadow-2xl animate-in zoom-in-95 duration-700 relative overflow-hidden">
                  <div className="absolute top-0 right-0 p-8 opacity-[0.03] scale-150 rotate-12">
                    <ShieldCheck className="w-64 h-64 text-primary" />
                  </div>

                  <div className="relative z-10">
                    <div className="flex items-center justify-between mb-10">
                      <div className="flex items-center gap-5">
                        <div className="w-16 h-16 rounded-3xl bg-primary text-white flex items-center justify-center shadow-2xl shadow-primary/20 animate-in spin-in-12 duration-1000">
                          <CheckCircle2 className="w-9 h-9" />
                        </div>
                        <div>
                          <h3 className="text-3xl font-black tracking-tighter">Audit Verified</h3>
                          <p className="text-primary/60 font-bold uppercase tracking-widest text-[10px]">Verification ID: #EMS-{Math.floor(Math.random() * 10000)}</p>
                        </div>
                      </div>
                      <Button size="icon" variant="ghost" className="rounded-full hover:bg-primary/10 transition-all">
                        <ExternalLink className="w-5 h-5" />
                      </Button>
                    </div>

                    <div className="bg-background/60 backdrop-blur-md rounded-[2.5rem] p-8 border border-primary/10 shadow-inner group/report min-h-[400px]">
                      <div className="flex items-center justify-between mb-8 pb-4 border-b border-muted">
                        <span className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground/50">Official Certificate</span>
                        <div className="flex gap-1.5">
                          <div className="w-2 h-2 rounded-full bg-red-400"></div>
                          <div className="w-2 h-2 rounded-full bg-amber-400"></div>
                          <div className="w-2 h-2 rounded-full bg-green-400"></div>
                        </div>
                      </div>

                      <div className="prose prose-slate dark:prose-invert max-w-none">
                        <pre className="whitespace-pre-wrap font-mono text-[13px] leading-relaxed text-foreground/80 lowercase selection:bg-primary selection:text-white">
                          {auditReport}
                        </pre>
                      </div>

                      <div className="mt-12 flex items-center justify-center">
                        <div className="w-24 h-1 bg-gradient-to-r from-transparent via-primary/20 to-transparent"></div>
                      </div>
                    </div>

                    <div className="mt-10 flex flex-col sm:flex-row items-center justify-between gap-6">
                      <div className="flex items-center gap-3">
                        <div className="flex -space-x-2">
                          {[1, 2, 3].map(i => (
                            <div key={i} className="w-8 h-8 rounded-full border-2 border-background bg-muted overflow-hidden flex items-center justify-center text-[8px] font-black">
                              AI
                            </div>
                          ))}
                        </div>
                        <span className="text-xs font-bold text-muted-foreground">Certified by 3 Cognitive Models</span>
                      </div>

                      <Button
                        variant="secondary"
                        onClick={() => {
                          setAuditState('idle');
                          setAuditReport(null);
                          setFiles([]);
                          setCurrentStepIndex(0);
                        }}
                        className="bg-foreground text-background hover:bg-primary hover:text-white h-14 px-8 rounded-2xl font-black text-sm transition-all shadow-xl shadow-black/10 active:scale-95"
                      >
                        Initiate New Audit Cycle
                      </Button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
