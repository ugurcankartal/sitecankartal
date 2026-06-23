import React from "react";
import { motion } from "motion/react";
import { Heart, Github, Linkedin, Mail, Globe } from "lucide-react";
import { useState, useEffect } from "react";
import { api, UserInfo, UserSocialLink } from "../services/api";
import { getIconOrDefault } from "../utils/iconMapper";

export function Footer() {
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const currentYear = new Date().getFullYear();

  useEffect(() => {
    const fetchUserInfo = async () => {
      try {
        const data = await api.getUserInfo();
        setUserInfo(data);
      } catch (error) {
        console.error("Failed to fetch user info:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchUserInfo();
  }, []);

  const socialLinks = userInfo?.social_links || [];

  return (
    <footer className="bg-slate-950 border-t border-cyan-500/20 relative overflow-hidden">
      {/* Background gradient effect */}
      <div className="absolute inset-0 bg-gradient-to-t from-cyan-500/5 via-transparent to-transparent" />
      
      <div className="container mx-auto px-6 py-12 relative z-10">
        <div className="max-w-6xl mx-auto">
          {/* Main Footer Content */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            {/* Brand Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="space-y-4"
            >
              <h3 className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                {userInfo?.full_name || "Portfolio"}
              </h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                {userInfo?.bio || "Full-Stack & DevOps Engineer"}
              </p>
            </motion.div>

            {/* Quick Links */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="space-y-4"
            >
              <h4 className="text-white font-semibold">Quick Links</h4>
              <ul className="space-y-2">
                <li>
                  <a
                    href="#home"
                    className="text-slate-400 hover:text-cyan-400 transition-colors text-sm"
                  >
                    Home
                  </a>
                </li>
                <li>
                  <a
                    href="#about"
                    className="text-slate-400 hover:text-cyan-400 transition-colors text-sm"
                  >
                    About
                  </a>
                </li>
                <li>
                  <a
                    href="#projects"
                    className="text-slate-400 hover:text-cyan-400 transition-colors text-sm"
                  >
                    Projects
                  </a>
                </li>
                <li>
                  <a
                    href="#contact"
                    className="text-slate-400 hover:text-cyan-400 transition-colors text-sm"
                  >
                    Contact
                  </a>
                </li>
              </ul>
            </motion.div>

            {/* Social Links */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="space-y-4"
            >
              <h4 className="text-white font-semibold">Connect</h4>
              {socialLinks.length > 0 ? (
                <div className="flex gap-3">
                  {socialLinks.map((link: UserSocialLink) => {
                    const Icon = getIconOrDefault(link.icon_name, Globe, link.platform);
                    return (
                      <motion.a
                        key={link.id}
                        href={link.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        whileHover={{ scale: 1.1, y: -3 }}
                        whileTap={{ scale: 0.95 }}
                        className="p-3 bg-slate-800/50 rounded-lg border border-slate-700 hover:border-cyan-500/50 transition-all"
                        title={link.platform}
                      >
                        <Icon className="w-5 h-5 text-cyan-400" />
                      </motion.a>
                    );
                  })}
                </div>
              ) : (
                <p className="text-slate-500 text-sm">No social links available</p>
              )}
            </motion.div>
          </div>

          {/* Bottom Bar */}
          <div className="border-t border-slate-800 pt-8">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              <motion.p
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true }}
                className="text-slate-400 flex items-center gap-2 text-sm"
              >
                Made with{" "}
                <motion.span
                  animate={{
                    scale: [1, 1.2, 1],
                  }}
                  transition={{
                    duration: 1,
                    repeat: Infinity,
                    ease: "easeInOut",
                  }}
                >
                  <Heart className="w-4 h-4 text-pink-500 fill-pink-500" />
                </motion.span>{" "}
                by{" "}
                <span className="text-cyan-400 font-semibold">
                  {userInfo?.full_name || "Portfolio Owner"}
                </span>
              </motion.p>

              <motion.p
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true }}
                className="text-slate-400 text-sm"
              >
                © {currentYear} All rights reserved
              </motion.p>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}