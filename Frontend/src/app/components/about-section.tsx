import React from "react";
import { motion, useInView } from "motion/react";
import { useRef, useState, useEffect } from "react";
import {
  Code2,
  Server,
  Cloud,
  Database,
  Terminal,
  Rocket,
  Award,
  Briefcase,
} from "lucide-react";
import { api, TimelineEntry, Skill, AboutSectionConfig } from "../services/api";
import { getIconOrDefault } from "../utils/iconMapper";

export function AboutSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, amount: 0.2 });
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [timeline, setTimeline] = useState<TimelineEntry[]>([]);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [aboutConfig, setAboutConfig] = useState<AboutSectionConfig | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [timelineData, skillsData, aboutData] = await Promise.all([
          api.getTimeline(),
          api.getSkills(),
          api.getAboutSection(),
        ]);
        setTimeline(timelineData);
        setSkills(skillsData);
        setAboutConfig(aboutData);
      } catch (error) {
        console.error("Failed to fetch about data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <section
      id="about"
      ref={ref}
      className="min-h-screen py-20 bg-gradient-to-b from-slate-950 to-slate-900 relative overflow-hidden"
    >
      {/* Background grid pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(6,182,212,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(6,182,212,0.03)_1px,transparent_1px)] bg-[size:50px_50px]" />

      <div className="container mx-auto px-6 relative z-10">
        {/* Section Title */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl md:text-6xl mb-4 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
            {aboutConfig?.title || "My Journey"}
          </h2>
          {aboutConfig?.subtitle && (
            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
              {aboutConfig.subtitle}
            </p>
          )}
        </motion.div>

        {/* Interactive Timeline */}
        <div className="max-w-6xl mx-auto mb-20">
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-1/2 transform -translate-x-1/2 h-full w-1 bg-gradient-to-b from-cyan-500 via-purple-500 to-pink-500 hidden lg:block" />

            {timeline.map((item, index) => {
              const Icon = getIconOrDefault(item.icon_name, Code2);
              const isLeft = index % 2 === 0;

              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: isLeft ? -50 : 50 }}
                  animate={isInView ? { opacity: 1, x: 0 } : {}}
                  transition={{ duration: 0.6, delay: index * 0.2 }}
                  className="relative mb-12 lg:mb-16"
                  onMouseEnter={() => setHoveredIndex(index)}
                  onMouseLeave={() => setHoveredIndex(null)}
                >
                  <div
                    className={`flex flex-col lg:flex-row items-center gap-8 ${
                      isLeft ? "lg:flex-row-reverse" : ""
                    }`}
                  >
                    {/* Content Card */}
                    <motion.div
                      whileHover={{ scale: 1.02, y: -5 }}
                      transition={{ type: "spring", stiffness: 300 }}
                      className={`w-full lg:w-5/12 bg-slate-800/50 backdrop-blur-sm border rounded-xl p-6 ${
                        hoveredIndex === index
                          ? "border-cyan-500 shadow-lg shadow-cyan-500/20"
                          : "border-slate-700"
                      } transition-all duration-300`}
                    >
                      <div className="flex items-start gap-4 mb-3">
                        <div
                          className={`p-3 rounded-lg ${
                            hoveredIndex === index
                              ? "bg-gradient-to-br from-cyan-500 to-purple-500"
                              : "bg-slate-700"
                          } transition-all duration-300`}
                        >
                          <Icon className="w-6 h-6 text-white" />
                        </div>
                        <div>
                          <h3 className="text-xl text-cyan-400 mb-1">
                            {item.title}
                          </h3>
                          <p className="text-slate-400">{item.company}</p>
                        </div>
                      </div>

                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{
                          height: hoveredIndex === index ? "auto" : 0,
                          opacity: hoveredIndex === index ? 1 : 0,
                        }}
                        transition={{ duration: 0.3 }}
                        className="overflow-hidden"
                      >
                        {item.description && (
                          <p className="text-slate-300 mb-3">{item.description}</p>
                        )}
                        {item.skills && item.skills.length > 0 && (
                          <div className="flex flex-wrap gap-2">
                            {item.skills.map((skill) => (
                              <span
                                key={skill}
                                className="px-3 py-1 text-sm bg-cyan-500/10 text-cyan-400 rounded-full border border-cyan-500/30"
                              >
                                {skill}
                              </span>
                            ))}
                          </div>
                        )}
                      </motion.div>
                    </motion.div>

                    {/* Year Badge */}
                    <motion.div
                      animate={{
                        scale: hoveredIndex === index ? 1.2 : 1,
                        rotate: hoveredIndex === index ? 360 : 0,
                      }}
                      transition={{ duration: 0.5 }}
                      className="w-20 h-20 rounded-full bg-gradient-to-br from-cyan-500 to-purple-500 flex items-center justify-center text-white text-lg font-bold shadow-lg z-10"
                    >
                      {item.year}
                    </motion.div>

                    {/* Spacer for layout */}
                    <div className="hidden lg:block w-5/12" />
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* Skills Progress Bars */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="max-w-4xl mx-auto"
        >
          <h3 className="text-3xl text-center mb-8 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
            {aboutConfig?.skills_title || "Core Competencies"}
          </h3>
          <div className="grid md:grid-cols-2 gap-6">
            {skills.map((skill, index) => (
              <div key={skill.id} className="space-y-2">
                <div className="flex justify-between text-slate-300">
                  <span>{skill.name}</span>
                  <span className="text-cyan-400">{skill.level}%</span>
                </div>
                <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={isInView ? { width: `${skill.level}%` } : {}}
                    transition={{ duration: 1, delay: 1 + index * 0.1 }}
                    className={`h-full bg-gradient-to-r ${
                      skill.color === "cyan"
                        ? "from-cyan-500 to-cyan-400"
                        : skill.color === "purple"
                        ? "from-purple-500 to-purple-400"
                        : "from-pink-500 to-pink-400"
                    } rounded-full`}
                  />
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
