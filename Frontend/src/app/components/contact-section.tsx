import React from "react";
import { motion, useInView } from "motion/react";
import { useRef, useState, useEffect } from "react";
import {
  Mail,
  Phone,
  MapPin,
  Send,
  Github,
  Linkedin,
  Twitter,
  Globe,
} from "lucide-react";
import { api, Profile, ContactFormData, UserInfo } from "../services/api";
import { getIconOrDefault } from "../utils/iconMapper";

export function ContactSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, amount: 0.2 });
  const [focusedField, setFocusedField] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    subject: "",
    message: "",
  });
  const [profile, setProfile] = useState<Profile | null>(null);
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

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
      }
    };

    fetchData();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setSubmitError(null);
    setSubmitSuccess(false);

    try {
      await api.submitContact(formData as ContactFormData);
      setSubmitSuccess(true);
      setFormData({
        name: "",
        email: "",
        subject: "",
        message: "",
      });
      setTimeout(() => setSubmitSuccess(false), 5000);
    } catch (error) {
      setSubmitError("Failed to send message. Please try again.");
      console.error("Form submission error:", error);
    } finally {
      setSubmitting(false);
    }
  };

  // Use user info (project owner) for contact info, fallback to profile if user info not available
  const contactInfo = userInfo
    ? [
        {
          icon: Mail,
          label: "Email",
          value: userInfo.email || "",
          href: userInfo.email ? `mailto:${userInfo.email}` : "#",
        },
        {
          icon: Phone,
          label: "Phone",
          value: userInfo.phone || "",
          href: userInfo.phone ? `tel:${userInfo.phone}` : "#",
        },
        {
          icon: MapPin,
          label: "Location",
          value: userInfo.location || "",
          href: "#",
        },
      ].filter((item) => item.value) // Only show items with values
    : profile
    ? [
        {
          icon: Mail,
          label: "Email",
          value: profile.email || "",
          href: profile.email ? `mailto:${profile.email}` : "#",
        },
        {
          icon: Phone,
          label: "Phone",
          value: profile.phone || "",
          href: profile.phone ? `tel:${profile.phone}` : "#",
        },
        {
          icon: MapPin,
          label: "Location",
          value: profile.location || "",
          href: "#",
        },
      ].filter((item) => item.value) // Only show items with values
    : [];

  // Use user's social links first, fallback to profile's social links
  const socialLinks = userInfo?.social_links && userInfo.social_links.length > 0
    ? userInfo.social_links.map((link) => {
        const Icon = getIconOrDefault(link.icon_name, Globe, link.platform);
        return {
          name: link.platform,
          icon: Icon,
          href: link.url,
          color: "hover:text-cyan-400",
        };
      })
    : profile?.social_links && profile.social_links.length > 0
    ? profile.social_links.map((link) => {
        const Icon = getIconOrDefault(link.icon_name, Globe, link.platform);
        return {
          name: link.platform,
          icon: Icon,
          href: link.url,
          color: "hover:text-cyan-400",
        };
      })
    : [];

  return (
    <section
      id="contact"
      ref={ref}
      className="min-h-screen py-20 bg-gradient-to-b from-slate-950 to-slate-900 relative overflow-hidden"
    >
      {/* Background Effects */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(6,182,212,0.1),transparent_50%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_20%,rgba(168,85,247,0.1),transparent_50%)]" />

      <div className="container mx-auto px-6 relative z-10">
        {/* Section Title */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl md:text-6xl mb-4 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
            Get In Touch
          </h2>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto">
            Have a project in mind? Let's collaborate and build something amazing together.
          </p>
        </motion.div>

        <div className="max-w-6xl mx-auto grid lg:grid-cols-5 gap-12">
          {/* Contact Info & Social Links */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="lg:col-span-2 space-y-8"
          >
            {/* Contact Information */}
            {contactInfo.length > 0 && (
              <div className="space-y-6">
                {contactInfo.map((item, index) => {
                  const Icon = item.icon;
                  return (
                    <motion.a
                      key={item.label}
                      href={item.href}
                      initial={{ opacity: 0, x: -20 }}
                      animate={isInView ? { opacity: 1, x: 0 } : {}}
                      transition={{ duration: 0.6, delay: 0.3 + index * 0.1 }}
                      whileHover={{ x: 10 }}
                      className="flex items-center gap-4 p-4 bg-slate-800/50 backdrop-blur-sm rounded-lg border border-slate-700 hover:border-cyan-500/50 transition-all group"
                    >
                      <div className="p-3 rounded-lg bg-gradient-to-br from-cyan-500 to-purple-500 group-hover:scale-110 transition-transform">
                        <Icon className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <p className="text-sm text-slate-400">{item.label}</p>
                        <p className="text-white group-hover:text-cyan-400 transition-colors">
                          {item.value}
                        </p>
                      </div>
                    </motion.a>
                  );
                })}
              </div>
            )}

            {/* Social Links */}
            {socialLinks.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: 0.6 }}
                className="pt-8"
              >
                <h3 className="text-2xl text-white mb-6">Connect With Me</h3>
                <div className="flex gap-4">
                  {socialLinks.map((social, index) => {
                    const Icon = social.icon;
                    return (
                      <motion.a
                        key={social.name}
                        href={social.href}
                        initial={{ opacity: 0, scale: 0 }}
                        animate={isInView ? { opacity: 1, scale: 1 } : {}}
                        transition={{
                          duration: 0.4,
                          delay: 0.7 + index * 0.1,
                          type: "spring",
                        }}
                        whileHover={{ scale: 1.2, rotate: 360 }}
                        whileTap={{ scale: 0.9 }}
                        className={`p-4 bg-slate-800 rounded-lg border border-slate-700 hover:border-cyan-500 text-slate-400 ${social.color} transition-all`}
                      >
                        <Icon size={24} />
                      </motion.a>
                    );
                  })}
                </div>
              </motion.div>
            )}

            {/* Decorative element */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={isInView ? { opacity: 1 } : {}}
              transition={{ duration: 1, delay: 0.8 }}
              className="relative h-64 rounded-2xl overflow-hidden border border-cyan-500/30"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/20 via-purple-500/20 to-pink-500/20" />
              <div className="absolute inset-0 backdrop-blur-3xl" />
              <motion.div
                animate={{
                  scale: [1, 1.4, 1],
                  rotate: [0, 360, 0],
                }}
                transition={{ duration: 12, repeat: Infinity, ease: "linear" }}
                className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-56 h-56 bg-gradient-to-br from-cyan-400 via-purple-500 to-pink-500 rounded-full blur-xl opacity-90"
                style={{
                  boxShadow: "0 0 60px rgba(6, 182, 212, 0.6), 0 0 100px rgba(168, 85, 247, 0.4)"
                }}
              />
              <motion.div
                animate={{
                  scale: [1, 1.2, 1],
                  rotate: [0, -360, 0],
                }}
                transition={{ duration: 18, repeat: Infinity, ease: "linear" }}
                className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-44 h-44 bg-gradient-to-br from-purple-400 to-cyan-500 rounded-full blur-lg opacity-80"
                style={{
                  boxShadow: "0 0 40px rgba(168, 85, 247, 0.5), 0 0 80px rgba(6, 182, 212, 0.3)"
                }}
              />
              <motion.div
                animate={{
                  scale: [0.8, 1, 0.8],
                  rotate: [0, 180, 360],
                }}
                transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
                className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-24 h-24 bg-gradient-to-br from-pink-400 to-cyan-400 rounded-full blur-md opacity-70"
                style={{
                  boxShadow: "0 0 30px rgba(236, 72, 153, 0.6)"
                }}
              />
            </motion.div>
          </motion.div>

          {/* Contact Form */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="lg:col-span-3"
          >
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Name Field */}
              <div className="relative">
                <motion.input
                  type="text"
                  id="name"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  onFocus={() => setFocusedField("name")}
                  onBlur={() => setFocusedField(null)}
                  className="w-full px-4 py-4 bg-slate-800/50 backdrop-blur-sm border rounded-lg text-white placeholder-transparent focus:outline-none transition-all peer"
                  placeholder="Your Name"
                  animate={{
                    borderColor:
                      focusedField === "name"
                        ? "rgb(6, 182, 212)"
                        : "rgb(51, 65, 85)",
                  }}
                />
                <motion.label
                  htmlFor="name"
                  className="absolute left-4 text-slate-400 transition-all pointer-events-none peer-placeholder-shown:top-4 peer-placeholder-shown:text-base peer-focus:top-0 peer-focus:text-xs peer-focus:text-cyan-400 peer-focus:-translate-y-3 peer-focus:bg-slate-900 peer-focus:px-2"
                  initial={false}
                  animate={{
                    top: formData.name ? 0 : "1rem",
                    fontSize: formData.name ? "0.75rem" : "1rem",
                    color:
                      focusedField === "name" || formData.name
                        ? "rgb(6, 182, 212)"
                        : "rgb(148, 163, 184)",
                    y: formData.name ? -12 : 0,
                  }}
                >
                  {formData.name || focusedField === "name" ? (
                    <span className="bg-slate-900 px-2">Your Name</span>
                  ) : (
                    "Your Name"
                  )}
                </motion.label>
                {focusedField === "name" && (
                  <motion.div
                    layoutId="focus-ring"
                    className="absolute inset-0 rounded-lg shadow-lg shadow-cyan-500/50 pointer-events-none"
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
              </div>

              {/* Email Field */}
              <div className="relative">
                <motion.input
                  type="email"
                  id="email"
                  value={formData.email}
                  onChange={(e) =>
                    setFormData({ ...formData, email: e.target.value })
                  }
                  onFocus={() => setFocusedField("email")}
                  onBlur={() => setFocusedField(null)}
                  className="w-full px-4 py-4 bg-slate-800/50 backdrop-blur-sm border rounded-lg text-white placeholder-transparent focus:outline-none transition-all peer"
                  placeholder="Your Email"
                  animate={{
                    borderColor:
                      focusedField === "email"
                        ? "rgb(168, 85, 247)"
                        : "rgb(51, 65, 85)",
                  }}
                />
                <motion.label
                  htmlFor="email"
                  className="absolute left-4 text-slate-400 transition-all pointer-events-none"
                  initial={false}
                  animate={{
                    top: formData.email ? 0 : "1rem",
                    fontSize: formData.email ? "0.75rem" : "1rem",
                    color:
                      focusedField === "email" || formData.email
                        ? "rgb(168, 85, 247)"
                        : "rgb(148, 163, 184)",
                    y: formData.email ? -12 : 0,
                  }}
                >
                  {formData.email || focusedField === "email" ? (
                    <span className="bg-slate-900 px-2">Your Email</span>
                  ) : (
                    "Your Email"
                  )}
                </motion.label>
                {focusedField === "email" && (
                  <motion.div
                    layoutId="focus-ring"
                    className="absolute inset-0 rounded-lg shadow-lg shadow-purple-500/50 pointer-events-none"
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
              </div>

              {/* Subject Field */}
              <div className="relative">
                <motion.input
                  type="text"
                  id="subject"
                  value={formData.subject}
                  onChange={(e) =>
                    setFormData({ ...formData, subject: e.target.value })
                  }
                  onFocus={() => setFocusedField("subject")}
                  onBlur={() => setFocusedField(null)}
                  className="w-full px-4 py-4 bg-slate-800/50 backdrop-blur-sm border rounded-lg text-white placeholder-transparent focus:outline-none transition-all peer"
                  placeholder="Subject"
                  animate={{
                    borderColor:
                      focusedField === "subject"
                        ? "rgb(236, 72, 153)"
                        : "rgb(51, 65, 85)",
                  }}
                />
                <motion.label
                  htmlFor="subject"
                  className="absolute left-4 text-slate-400 transition-all pointer-events-none"
                  initial={false}
                  animate={{
                    top: formData.subject ? 0 : "1rem",
                    fontSize: formData.subject ? "0.75rem" : "1rem",
                    color:
                      focusedField === "subject" || formData.subject
                        ? "rgb(236, 72, 153)"
                        : "rgb(148, 163, 184)",
                    y: formData.subject ? -12 : 0,
                  }}
                >
                  {formData.subject || focusedField === "subject" ? (
                    <span className="bg-slate-900 px-2">Subject</span>
                  ) : (
                    "Subject"
                  )}
                </motion.label>
                {focusedField === "subject" && (
                  <motion.div
                    layoutId="focus-ring"
                    className="absolute inset-0 rounded-lg shadow-lg shadow-pink-500/50 pointer-events-none"
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
              </div>

              {/* Message Field */}
              <div className="relative">
                <motion.textarea
                  id="message"
                  value={formData.message}
                  onChange={(e) =>
                    setFormData({ ...formData, message: e.target.value })
                  }
                  onFocus={() => setFocusedField("message")}
                  onBlur={() => setFocusedField(null)}
                  rows={6}
                  className="w-full px-4 py-4 bg-slate-800/50 backdrop-blur-sm border rounded-lg text-white placeholder-transparent focus:outline-none transition-all resize-none peer"
                  placeholder="Your Message"
                  animate={{
                    borderColor:
                      focusedField === "message"
                        ? "rgb(6, 182, 212)"
                        : "rgb(51, 65, 85)",
                  }}
                />
                <motion.label
                  htmlFor="message"
                  className="absolute left-4 text-slate-400 transition-all pointer-events-none"
                  initial={false}
                  animate={{
                    top: formData.message ? 0 : "1rem",
                    fontSize: formData.message ? "0.75rem" : "1rem",
                    color:
                      focusedField === "message" || formData.message
                        ? "rgb(6, 182, 212)"
                        : "rgb(148, 163, 184)",
                    y: formData.message ? -12 : 0,
                  }}
                >
                  {formData.message || focusedField === "message" ? (
                    <span className="bg-slate-900 px-2">Your Message</span>
                  ) : (
                    "Your Message"
                  )}
                </motion.label>
                {focusedField === "message" && (
                  <motion.div
                    layoutId="focus-ring"
                    className="absolute inset-0 rounded-lg shadow-lg shadow-cyan-500/50 pointer-events-none"
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
              </div>

              {/* Submit Button */}
              <motion.button
                type="submit"
                disabled={submitting}
                whileHover={{ scale: submitting ? 1 : 1.02 }}
                whileTap={{ scale: submitting ? 1 : 0.98 }}
                className="w-full py-4 bg-gradient-to-r from-cyan-500 to-purple-500 text-white rounded-lg font-semibold flex items-center justify-center gap-2 hover:shadow-lg hover:shadow-purple-500/50 transition-all group disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span>{submitting ? "Sending..." : "Send Message"}</span>
                <Send
                  size={20}
                  className="group-hover:translate-x-1 transition-transform"
                />
              </motion.button>

              {/* Success/Error Messages */}
              {submitSuccess && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 p-4 bg-green-500/20 border border-green-500/50 rounded-lg text-green-400"
                >
                  Message sent successfully!
                </motion.div>
              )}
              {submitError && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-400"
                >
                  {submitError}
                </motion.div>
              )}
            </form>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
