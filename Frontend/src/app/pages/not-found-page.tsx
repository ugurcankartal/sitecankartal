import React from "react";
import { motion } from "motion/react";
import { useNavigate } from "react-router";
import { Home, ArrowLeft, Search } from "lucide-react";
import { Navigation } from "../components/navigation";
import { Footer } from "../components/footer";

export function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-slate-950 text-white overflow-x-hidden">
      <Navigation />
      <main className="container mx-auto px-6 py-20 pt-32">
        <div className="max-w-4xl mx-auto text-center">
          {/* Animated 404 */}
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
              className="text-9xl md:text-[12rem] font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent"
            >
              404
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
              Page Not Found
            </h2>
            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
              Oops! The page you're looking for seems to have wandered off into
              the digital void. Let's get you back on track.
            </p>
          </motion.div>

          {/* Animated Search Icon */}
          <motion.div
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="mb-12 flex justify-center"
          >
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-full blur-2xl opacity-20 animate-pulse" />
              <div className="relative bg-slate-800/50 backdrop-blur-sm p-8 rounded-full border border-slate-700">
                <Search size={64} className="text-cyan-400" />
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
              onClick={() => navigate("/")}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-cyan-500 to-purple-500 text-white rounded-full hover:shadow-lg hover:shadow-purple-500/50 transition-all"
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

          {/* Decorative Elements */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
