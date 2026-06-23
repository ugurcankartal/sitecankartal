import React from "react";
import { motion } from "motion/react";
import { useNavigate } from "react-router";
import { AlertTriangle, Home, RefreshCw, ArrowLeft } from "lucide-react";
import { Navigation } from "../components/navigation";
import { Footer } from "../components/footer";

export function ErrorPage() {
  const navigate = useNavigate();

  const handleRefresh = () => {
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white overflow-x-hidden">
      <Navigation />
      <main className="container mx-auto px-6 py-20 pt-32">
        <div className="max-w-4xl mx-auto text-center">
          {/* Animated 500 */}
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mb-8"
          >
            <motion.h1
              initial={{ scale: 0.5 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-9xl md:text-[12rem] font-bold bg-gradient-to-r from-red-400 via-orange-400 to-yellow-400 bg-clip-text text-transparent"
            >
              500
            </motion.h1>
          </motion.div>

          {/* Error Message */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="mb-12"
          >
            <h2 className="text-4xl md:text-5xl mb-4 text-white">
              Internal Server Error
            </h2>
            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
              Something went wrong on our end. We're working to fix the issue.
              Please try again in a few moments.
            </p>
          </motion.div>

          {/* Animated Alert Icon */}
          <motion.div
            initial={{ opacity: 0, scale: 0, rotate: -180 }}
            animate={{ opacity: 1, scale: 1, rotate: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="mb-12 flex justify-center"
          >
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-red-500 to-orange-500 rounded-full blur-2xl opacity-20 animate-pulse" />
              <div className="relative bg-slate-800/50 backdrop-blur-sm p-8 rounded-full border border-red-500/30">
                <AlertTriangle size={64} className="text-red-400" />
              </div>
            </div>
          </motion.div>

          {/* Action Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="flex flex-col sm:flex-row gap-4 justify-center items-center"
          >
            <motion.button
              onClick={handleRefresh}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-red-500 to-orange-500 text-white rounded-full hover:shadow-lg hover:shadow-red-500/50 transition-all"
            >
              <RefreshCw size={20} />
              <span>Refresh Page</span>
            </motion.button>

            <motion.button
              onClick={() => navigate("/")}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="inline-flex items-center gap-2 px-8 py-4 bg-slate-800/50 backdrop-blur-sm border border-slate-700 text-white rounded-full hover:border-cyan-500/50 transition-all"
            >
              <Home size={20} />
              <span>Go Home</span>
            </motion.button>

            <motion.button
              onClick={() => navigate(-1)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="inline-flex items-center gap-2 px-8 py-4 bg-slate-800/50 backdrop-blur-sm border border-slate-700 text-white rounded-full hover:border-cyan-500/50 transition-all"
            >
              <ArrowLeft size={20} />
              <span>Go Back</span>
            </motion.button>
          </motion.div>

          {/* Technical Details (Optional - can be expanded) */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.8 }}
            className="mt-12 p-6 bg-slate-800/30 backdrop-blur-sm border border-slate-700/50 rounded-lg max-w-2xl mx-auto"
          >
            <p className="text-sm text-slate-500">
              If this problem persists, please contact support or try again
              later.
            </p>
          </motion.div>

          {/* Decorative Elements */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-red-500/10 rounded-full blur-3xl" />
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-orange-500/10 rounded-full blur-3xl" />
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
