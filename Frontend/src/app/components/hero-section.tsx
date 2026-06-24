import React from "react";
import { motion } from "motion/react";
import { useEffect, useState } from "react";
import { Github, Linkedin, Mail } from "lucide-react";
import { ParticleBackground } from "./particle-background";
import { api, Profile, UserInfo } from "../services/api";
import { getIconOrDefault } from "../utils/iconMapper";

export function HeroSection() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [profileData, userData] = await Promise.all([
          api.getProfile(),
          api.getUserInfo(),
        ]);
        setProfile(profileData);
        setUserInfo(userData);
      } catch (error) {
        console.error("Failed to fetch data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading || (!profile && !userInfo)) {
    return (
      <section
        id="home"
        className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-slate-950 via-purple-950/20 to-slate-950"
      >
        <ParticleBackground />
      </section>
    );
  }

  // Determine which data to use: UserInfo (project owner) first, then Profile
  const displayName = userInfo?.full_name || profile?.name || "Portfolio Owner";
  const displayTitle = profile?.title || userInfo?.bio || "Full-Stack Developer";
  const displayDescription = userInfo?.bio || profile?.description || "";
  
  // Build image URL - if user has profile_image_url, use it with API base URL
  let displayImage = "";
  if (userInfo?.profile_image_url) {
    // Use relative path - API already returns correct path
    displayImage = userInfo.profile_image_url;
  } else if (profile?.profile_image_url) {
    displayImage = profile.profile_image_url;
  }

  // Use user's social links first, fallback to profile's social links
  const socialLinksWithIcons = userInfo?.social_links && userInfo.social_links.length > 0
    ? userInfo.social_links.map((link) => {
        const Icon = getIconOrDefault(link.icon_name, Mail, link.platform);
        return {
          id: link.id,
          platform: link.platform,
          url: link.url,
          icon: Icon,
        };
      })
    : profile?.social_links && profile.social_links.length > 0
    ? profile.social_links.map((link) => {
        const Icon = getIconOrDefault(link.icon_name, Mail, link.platform);
        return {
          id: link.id,
          platform: link.platform,
          url: link.url,
          icon: Icon,
        };
      })
    : [];

  return (
    <section
      id="home"
      className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-slate-950 via-purple-950/20 to-slate-950"
    >
      {/* Animated Background */}
      <ParticleBackground />
      
      {/* Content */}
      <div className="relative z-10 container mx-auto px-6 py-20">
        <div className="max-w-5xl mx-auto text-center">
          {/* Profile Image with animated glow */}
          {displayImage && (
            <motion.div
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, ease: "easeOut" }}
              className="mb-8 inline-block relative"
            >
              <motion.div
                animate={{
                  boxShadow: [
                    "0 0 20px rgba(6, 182, 212, 0.3)",
                    "0 0 40px rgba(168, 85, 247, 0.4)",
                    "0 0 20px rgba(6, 182, 212, 0.3)",
                  ],
                }}
                transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                className="w-40 h-40 rounded-full overflow-hidden border-4 border-cyan-500/50 relative"
              >
                <img
                  src={displayImage}
                  alt={displayName}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-tr from-cyan-500/10 to-purple-500/10" />
              </motion.div>
            </motion.div>
          )}

          {/* Name and Title with staggered animation */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <motion.h1
              className="text-6xl md:text-7xl lg:text-8xl mb-4 bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 1, delay: 0.4 }}
            >
              {displayName}
            </motion.h1>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="mb-6"
          >
            <h2 className="text-2xl md:text-3xl lg:text-4xl text-cyan-400 mb-4">
              {displayTitle}
            </h2>
            {displayDescription && (
              <p className="text-lg md:text-xl text-slate-300 max-w-2xl mx-auto">
                {displayDescription}
              </p>
            )}
          </motion.div>

          {/* Social Links with hover animations */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="flex gap-4 justify-center items-center mt-8"
          >
            {socialLinksWithIcons.map((social, index) => {
              const Icon = social.icon;
              return (
                <motion.a
                  key={social.id}
                  href={social.url}
                  whileHover={{ scale: 1.1, y: -5 }}
                  whileTap={{ scale: 0.95 }}
                  transition={{ type: "spring", stiffness: 400, damping: 17 }}
                  className="p-4 rounded-lg bg-slate-800/50 backdrop-blur-sm border border-cyan-500/30 hover:border-cyan-500 transition-colors"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  style={{ transitionDelay: `${index * 100}ms` }}
                  title={social.platform}
                >
                  <Icon className="w-6 h-6 text-cyan-400" />
                </motion.a>
              );
            })}
          </motion.div>

          {/* Scroll Indicator */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 1 }}
            className="mt-16"
          >
            <motion.div
              animate={{ y: [0, 10, 0] }}
              transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
              className="w-6 h-10 border-2 border-cyan-500 rounded-full mx-auto flex justify-center"
            >
              <motion.div
                animate={{ y: [0, 12, 0] }}
                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                className="w-1.5 h-3 bg-cyan-500 rounded-full mt-2"
              />
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
