"use client";
// ityjbi
import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  UploadCloud,
  CheckCircle,
  AlertCircle,
  FileText,
  Sparkles,
} from "lucide-react";
import { useDropzone } from "react-dropzone";
import { useRouter } from "next/navigation";

export default function CvAnalyzerPage() {
  const router = useRouter();
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isRunningNLP, setIsRunningNLP] = useState(false);

  // حالة تتبع حركة الماوس للتأثير ثلاثي الأبعاد الحقيقي
  const [tilt, setTilt] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // حساب زاوية الميلان بناءً على موقع الماوس (بحد أقصى 15 درجة)
    const rotateX = (y / rect.height - 0.5) * -15;
    const rotateY = (x / rect.width - 0.5) * 15;

    setTilt({ x: rotateX, y: rotateY });
  };

  const handleMouseLeave = () => {
    setTilt({ x: 0, y: 0 });
  };

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    setError(null);
    setResult(null);

    if (rejectedFiles && rejectedFiles.length > 0) {
      setError("Please upload a valid PDF or DOCX file under 5MB.");
      return;
    }

    if (acceptedFiles && acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        [".docx"],
      "application/msword": [".doc"],
      "text/plain": [".txt"],
    },
    maxSize: 5242880, // 5MB
    maxFiles: 1,
  });

  const startAnalysis = async () => {
    if (!file) return;
    const projectId = localStorage.getItem("project_id") || "default_id";
    setIsUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      // 1) Upload
      const uploadResponse = await fetch(
        `http://127.0.0.1:5000/api/v1/data/upload/${projectId}`,
        {
          method: "POST",
          headers: { accept: "application/json" },
          body: formData,
        },
      );

      if (!uploadResponse.ok) {
        throw new Error(`Upload failed with status: ${uploadResponse.status}`);
      }

      const uploadData = await uploadResponse.json();
      const fileId = uploadData["file id"];

      // 2) Process
      const processResponse = await fetch(
        `http://127.0.0.1:5000/api/v1/data/process/${projectId}`,
        {
          method: "POST",
          headers: {
            accept: "application/json",
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ fileId: fileId }),
        },
      );

      if (!processResponse.ok) {
        throw new Error(
          `Process failed with status: ${processResponse.status}`,
        );
      }

      const processData = await processResponse.json();

      setResult({
        status: "success",
        message: uploadData.signal || "file_upload_success",
        fileId,
        fileName: file.name,
        processStatus: processData?.signal || "processing_done",
      });
    } catch (err) {
      console.error("Upload error:", err);
      setError("Failed to analyze resume. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  const runAllAnalysis = async () => {
    const projectId = localStorage.getItem("project_id") || "default_id";
    try {
      setIsRunningNLP(true);
      setError(null);

      const response = await fetch(
        `http://127.0.0.1:5000/api/v1/nlp/index/run_all/${projectId}`,
        {
          method: "POST",
          headers: {
            accept: "application/json",
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            skill_request: { user_skill: ["python", "fastapi"] },
            gap_request: { user_gap_skill: ["docker", "kubernetes"] },
          }),
        },
      );

      if (!response.ok) {
        const errText = await response.text();
        console.error("Run All Error:", errText);
        throw new Error(`Run all failed: ${response.status}`);
      }

      const data = await response.json();
      setResult((prev) => ({ ...prev, nlpResult: data }));
    } catch (err) {
      console.error(err);
      setError("Failed to run NLP analysis.");
    } finally {
      setIsRunningNLP(false);
    }
  };

  const resetState = () => {
    setFile(null);
    setResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen relative flex flex-col items-center justify-center max-w-5xl mx-auto py-10 overflow-hidden">
      {/* Aurora Background Effect */}
      {/* <div className="absolute inset-0 z-[-1] overflow-hidden pointer-events-none opacity-40 mix-blend-screen">
        <div className="absolute top-[-10%] left-[-10%] w-[50vw] h-[50vw] rounded-full bg-primary/40 blur-[120px] animate-blob" />
        <div className="absolute top-[20%] right-[-10%] w-[45vw] h-[45vw] rounded-full bg-blue-500/30 blur-[120px] animate-blob animation-delay-2000" />
        <div className="absolute bottom-[-20%] left-[20%] w-[60vw] h-[60vw] rounded-full bg-purple-500/30 blur-[120px] animate-blob animation-delay-4000" />
      </div> */}

      {/* Floating Header */}
      <motion.div
        className="w-full text-center mb-10 z-10"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: [0, -10, 0] }}
        transition={{
          opacity: { duration: 0.8 },
          y: { duration: 4, repeat: Infinity, ease: "easeInOut" },
        }}
      >
        <div className="inline-flex items-center justify-center space-x-3 mb-4">
          <Sparkles className="w-8 h-8 text-primary animate-pulse" />
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-primary via-blue-500 to-purple-500 pb-1">
            CV Neural Analyzer
          </h1>
        </div>
        <p className="text-muted-foreground max-w-xl mx-auto text-lg backdrop-blur-sm bg-background/30 p-2 rounded-xl">
          Upload your resume. Our parsing engine will extract your structural
          data, identify hard skills, and map your trajectory.
        </p>
      </motion.div>

      <div className="w-full relative z-10 px-4">
        <AnimatePresence mode="wait">
          {/* Upload State */}
          {!isUploading && !result && (
            <motion.div
              key="upload"
              initial={{ opacity: 0, scale: 0.9, filter: "blur(10px)" }}
              animate={{
                opacity: 1,
                scale: 1,
                filter: "blur(0px)",
                rotateX: tilt.x,
                rotateY: tilt.y,
              }}
              exit={{ opacity: 0, scale: 0.95, filter: "blur(10px)" }}
              transition={{ type: "spring", stiffness: 300, damping: 20 }}
              className="glass p-10 md:p-16 rounded-[2.5rem] w-full border border-primary/20 bg-background/60 backdrop-blur-xl shadow-2xl flex flex-col items-center justify-center text-center will-change-transform"
              style={{ transformStyle: "preserve-3d", perspective: "1000px" }}
              onMouseMove={handleMouseMove}
              onMouseLeave={handleMouseLeave}
            >
              <div
                {...getRootProps()}
                className={`w-full max-w-xl mx-auto p-12 border-2 border-dashed rounded-3xl cursor-pointer transition-all duration-300 relative overflow-hidden group ${
                  isDragActive
                    ? "border-primary bg-primary/10 scale-105"
                    : "border-primary/30 hover:border-primary/60 hover:bg-primary/5 hover:shadow-[0_0_30px_rgba(var(--primary),0.1)]"
                }`}
                style={{ transform: "translateZ(30px)" }} // 3D Pop inside the card
              >
                <input {...getInputProps()} />

                {/* Energy Pulse Icon */}
                <div className="relative w-24 h-24 mx-auto mb-8 flex items-center justify-center">
                  <motion.div
                    className="absolute inset-0 rounded-full bg-primary/20"
                    animate={{ scale: [1, 1.8, 1], opacity: [0.8, 0, 0.8] }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      ease: "easeInOut",
                    }}
                  />
                  <motion.div
                    className="absolute inset-2 rounded-full bg-primary/30"
                    animate={{ scale: [1, 1.4, 1], opacity: [1, 0, 1] }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      ease: "easeInOut",
                      delay: 0.2,
                    }}
                  />
                  <div className="relative z-10 w-20 h-20 rounded-full bg-background border border-primary/30 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                    <UploadCloud className="w-10 h-10 text-primary" />
                  </div>
                </div>

                <h3 className="text-2xl font-bold mb-3 bg-clip-text text-transparent bg-gradient-to-b from-foreground to-foreground/70">
                  Initialize Parsing Sequence
                </h3>
                <p className="text-muted-foreground mb-4">
                  Drag & Drop your resume here, or click to select
                </p>
                <div className="inline-block bg-muted/50 px-4 py-1.5 rounded-full border border-border/50">
                  <p className="text-xs text-foreground/70 font-semibold tracking-wider">
                    SUPPORTED: PDF, DOCX (Max 5MB)
                  </p>
                </div>

                {file && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-8 flex items-center justify-center space-x-3 text-primary font-medium bg-primary/10 border border-primary/30 px-6 py-3 rounded-xl shadow-inner"
                  >
                    <FileText className="w-5 h-5" />
                    <span className="truncate max-w-[200px]">{file.name}</span>
                    <CheckCircle className="w-4 h-4 text-green-500 ml-2" />
                  </motion.div>
                )}
              </div>

              <motion.button
                whileHover={{ scale: file ? 1.05 : 1 }}
                whileTap={{ scale: file ? 0.95 : 1 }}
                onClick={startAnalysis}
                disabled={!file}
                style={{ transform: "translateZ(40px)" }}
                className="relative overflow-hidden mt-10 w-full max-w-md px-8 py-4 bg-primary text-primary-foreground font-bold text-lg rounded-2xl disabled:opacity-50 transition-all shadow-[0_10px_40px_-10px_rgba(var(--primary),0.5)] hover:shadow-[0_10px_40px_-5px_rgba(var(--primary),0.8)] disabled:hover:shadow-none"
              >
                <span className="relative z-10">Analyze Target Document</span>
                {/* Button Shine Effect */}
                {file && (
                  <motion.div
                    className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/20 to-transparent z-0"
                    animate={{ translateX: ["-100%", "200%"] }}
                    transition={{
                      duration: 1.5,
                      repeat: Infinity,
                      repeatDelay: 3,
                    }}
                  />
                )}
              </motion.button>

              {error && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  className="mt-6 flex items-center text-sm text-red-500 bg-red-500/10 px-6 py-3 rounded-xl border border-red-500/20"
                >
                  <AlertCircle className="w-5 h-5 mr-3 flex-shrink-0" />
                  {error}
                </motion.div>
              )}
            </motion.div>
          )}

          {/* Skeleton Processing State */}
          {isUploading && (
            <motion.div
              key="processing"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="glass relative overflow-hidden p-10 md:p-16 rounded-[2.5rem] w-full border border-primary/30 bg-background/60 backdrop-blur-xl shadow-2xl flex flex-col space-y-10"
            >
              {/* AI Scanning Laser Effect */}
              <motion.div
                className="absolute left-0 right-0 h-1 bg-gradient-to-r from-transparent via-primary to-transparent shadow-[0_0_15px_theme(colors.primary.DEFAULT)] z-50 opacity-70"
                animate={{ top: ["0%", "100%", "0%"] }}
                transition={{ duration: 3, ease: "linear", repeat: Infinity }}
              />

              <div className="text-center mb-2 relative z-10">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                  className="w-16 h-16 mx-auto mb-6 border-4 border-primary/20 border-t-primary rounded-full"
                />
                <h3 className="text-2xl font-bold tracking-widest uppercase text-transparent bg-clip-text bg-gradient-to-r from-primary to-blue-400 animate-pulse">
                  Neural Pipeline Active
                </h3>
                <p className="text-muted-foreground font-mono text-sm mt-3">
                  Extracting structural entities & parsing vectors...
                </p>
              </div>

              {/* Enhanced Skeleton Bars */}
              <div className="space-y-6 w-full max-w-xl mx-auto relative z-10">
                <div className="space-y-4">
                  <div className="h-5 w-1/4 bg-primary/20 rounded-md animate-pulse" />
                  <div className="h-4 w-full bg-muted/60 rounded-md animate-pulse animation-delay-200" />
                  <div className="h-4 w-5/6 bg-muted/60 rounded-md animate-pulse animation-delay-400" />
                  <div className="h-4 w-4/6 bg-muted/60 rounded-md animate-pulse animation-delay-600" />
                </div>

                <div className="space-y-4 pt-6">
                  <div className="h-5 w-1/3 bg-blue-500/20 rounded-md animate-pulse" />
                  <div className="h-28 w-full bg-muted/40 rounded-xl animate-pulse" />
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full max-w-xl mx-auto h-2 bg-muted/50 rounded-full overflow-hidden relative z-10">
                <motion.div
                  className="h-full bg-gradient-to-r from-primary via-blue-500 to-primary"
                  animate={{
                    x: ["-100%", "200%"],
                  }}
                  transition={{
                    duration: 2,
                    ease: "easeInOut",
                    repeat: Infinity,
                  }}
                  style={{ width: "50%" }}
                />
              </div>
            </motion.div>
          )}

          {/* Success State */}
          {result && (
            <motion.div
              key="success"
              initial={{ opacity: 0, scale: 0.5, y: 50 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              transition={{ type: "spring", damping: 15, stiffness: 200 }}
              className="glass relative overflow-hidden p-12 md:p-16 rounded-[2.5rem] w-full border border-green-500/40 bg-background/60 backdrop-blur-xl shadow-2xl flex flex-col items-center justify-center text-center"
            >
              {/* Confetti / Glow Background behind check */}
              <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-40 h-40 bg-green-500/20 rounded-full blur-[60px]" />

              <motion.div
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ type: "spring", delay: 0.2, bounce: 0.6 }}
                className="relative w-24 h-24 rounded-full bg-gradient-to-br from-green-400/20 to-green-600/20 flex items-center justify-center mb-8 border-2 border-green-500/50 shadow-[0_0_30px_rgba(34,197,94,0.3)]"
              >
                <CheckCircle className="w-12 h-12 text-green-500 drop-shadow-md" />
              </motion.div>

              <motion.h3
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="text-3xl font-extrabold mb-3 text-foreground"
              >
                Analysis Complete
              </motion.h3>

              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
                className="text-muted-foreground text-lg mb-3"
              >
                File Processed:{" "}
                <span className="font-semibold text-foreground">
                  {file?.name}
                </span>
              </motion.p>

              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="text-xs text-green-500 font-mono mb-10 bg-green-500/10 px-4 py-2 rounded-lg border border-green-500/20"
              >
                ID: {result.fileId}
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="flex flex-col sm:flex-row gap-4 w-full max-w-lg"
              >
                <button
                  onClick={resetState}
                  className="flex-1 px-6 py-4 border border-border rounded-xl text-sm font-semibold hover:bg-muted/80 transition-colors"
                >
                  Upload Another
                </button>
                <button
                  onClick={() => router.push("/results")}
                  className="flex-1 px-6 py-4 bg-primary text-primary-foreground rounded-xl text-sm font-bold shadow-lg shadow-primary/20 transition-all hover:bg-primary/90 hover:-translate-y-1"
                >
                  View Profile
                </button>
                <button
                  onClick={runAllAnalysis}
                  disabled={isRunningNLP}
                  className="flex-1 px-6 py-4 bg-blue-600 text-white rounded-xl text-sm font-bold shadow-lg shadow-blue-500/20 transition-all hover:bg-blue-500 hover:-translate-y-1 disabled:opacity-50 disabled:hover:translate-y-0"
                >
                  {isRunningNLP ? "Running..." : "Run Full NLP"}
                </button>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Global Styles for Animations */}
      <style jsx global>{`
        @keyframes blob {
          0% {
            transform: translate(0px, 0px) scale(1);
          }
          33% {
            transform: translate(30px, -50px) scale(1.1);
          }
          66% {
            transform: translate(-20px, 20px) scale(0.9);
          }
          100% {
            transform: translate(0px, 0px) scale(1);
          }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-200 {
          animation-delay: 0.2s;
        }
        .animation-delay-400 {
          animation-delay: 0.4s;
        }
        .animation-delay-600 {
          animation-delay: 0.6s;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  );
}
