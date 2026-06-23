import React from "react";
import { motion, useInView } from "motion/react";
import { useRef, useState, useEffect } from "react";
import {
  ExternalLink,
  Github,
  Cloud,
  Smartphone,
  ShoppingCart,
  BarChart3,
  Workflow,
  Database,
} from "lucide-react";
import { api, Project } from "../services/api";
import { getIconOrDefault } from "../utils/iconMapper";

export function ProjectsSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, amount: 0.1 });
  const [hoveredId, setHoveredId] = useState<number | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [dataLoaded, setDataLoaded] = useState(false);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const data = await api.getProjects();
        // Filter only active projects (status=true)
        // Backend already filters, but we add extra safety check
        const activeProjects = data.filter((project: Project) => {
          // Only include projects with status explicitly set to true
          return project.status === true;
        });
        setProjects(activeProjects);
        setDataLoaded(true);
      } catch (error) {
        console.error("Failed to fetch projects:", error);
        setDataLoaded(true);
      } finally {
        setLoading(false);
      }
    };

    fetchProjects();
  }, []);

  // Don't render section if there are no published projects
  // API already filters by status=true, so we just check if projects array is empty
  if (loading) {
    return null;
  }

  if (projects.length === 0) {
    return null;
  }

  return (
    <section
      id="projects"
      ref={ref}
      className="min-h-screen py-20 bg-gradient-to-b from-slate-900 to-slate-950 relative overflow-hidden"
    >
      {/* Background decoration */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,rgba(6,182,212,0.1),transparent_50%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_50%,rgba(168,85,247,0.1),transparent_50%)]" />

      <div className="container mx-auto px-6 relative z-10">
        {/* Section Title */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={dataLoaded ? (isInView ? { opacity: 1, y: 0 } : { opacity: 1, y: 0 }) : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl md:text-6xl mb-4 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
            Featured Projects
          </h2>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto">
            Showcase of innovative solutions and technical excellence
          </p>
        </motion.div>

        {/* Projects Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
          {projects.map((project, index) => {
            const Icon = getIconOrDefault(project.icon_name, Cloud);
            const gradient = project.gradient || "from-cyan-500 to-blue-500";

            return (
              <motion.div
                key={project.id}
                initial={{ opacity: 0, y: 50 }}
                animate={dataLoaded ? (isInView ? { opacity: 1, y: 0 } : { opacity: 1, y: 0 }) : {}}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                onMouseEnter={() => setHoveredId(project.id)}
                onMouseLeave={() => setHoveredId(null)}
                className="group relative"
              >
                {/* Card with 3D tilt effect on hover */}
                <motion.div
                  whileHover={{
                    y: -10,
                    rotateX: 5,
                    rotateY: 5,
                  }}
                  transition={{ type: "spring", stiffness: 300, damping: 20 }}
                  className="relative bg-slate-800/50 backdrop-blur-sm rounded-xl overflow-hidden border border-slate-700 hover:border-cyan-500/50 transition-all duration-300"
                  style={{
                    transformStyle: "preserve-3d",
                    perspective: 1000,
                  }}
                >
                  {/* Project Image */}
                  {project.image_url && (
                    <div className="relative h-48 overflow-hidden">
                      <motion.img
                        src={project.image_url}
                        alt={project.title}
                        className="w-full h-full object-cover"
                        animate={{
                          scale: hoveredId === project.id ? 1.1 : 1,
                        }}
                        transition={{ duration: 0.4 }}
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-slate-900 to-transparent" />

                      {/* Floating Icon */}
                      <motion.div
                        initial={{ y: 0 }}
                        animate={{
                          y: hoveredId === project.id ? -10 : 0,
                        }}
                        transition={{ duration: 0.3 }}
                        className={`absolute top-4 right-4 p-3 rounded-lg bg-gradient-to-br ${gradient} shadow-lg`}
                      >
                        <Icon className="w-6 h-6 text-white" />
                      </motion.div>
                    </div>
                  )}

                  {/* Floating Icon - Show when no image */}
                  {!project.image_url && (
                    <motion.div
                      initial={{ y: 0 }}
                      animate={{
                        y: hoveredId === project.id ? -10 : 0,
                      }}
                      transition={{ duration: 0.3 }}
                      className={`absolute top-4 right-4 p-3 rounded-lg bg-gradient-to-br ${gradient} shadow-lg`}
                    >
                      <Icon className="w-6 h-6 text-white" />
                    </motion.div>
                  )}

                  {/* Content */}
                  <div className="p-6">
                    <h3 className="text-2xl text-white mb-2 group-hover:text-cyan-400 transition-colors">
                      {project.title}
                    </h3>
                    <p className="text-slate-400 mb-4 line-clamp-2">
                      {project.description}
                    </p>

                    {/* Tech Stack Tags */}
                    <div className="flex flex-wrap gap-2 mb-4">
                      {project.tags.map((tag) => (
                        <motion.span
                          key={tag}
                          whileHover={{ scale: 1.05 }}
                          className="px-3 py-1 text-xs bg-cyan-500/10 text-cyan-400 rounded-full border border-cyan-500/30"
                        >
                          {tag}
                        </motion.span>
                      ))}
                    </div>

                    {/* Action Buttons */}
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{
                        opacity: hoveredId === project.id ? 1 : 0,
                        y: hoveredId === project.id ? 0 : 20,
                      }}
                      transition={{ duration: 0.3 }}
                      className="flex gap-3"
                    >
                      {project.github_url && (
                        <motion.a
                          href={project.github_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
                        >
                          <Github size={16} />
                          <span className="text-sm">Code</span>
                        </motion.a>
                      )}
                      {project.demo_url && (
                        <motion.a
                          href={project.demo_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-gradient-to-r ${gradient} text-white rounded-lg transition-all`}
                        >
                          <ExternalLink size={16} />
                          <span className="text-sm">Demo</span>
                        </motion.a>
                      )}
                    </motion.div>
                  </div>

                  {/* Glow effect on hover */}
                  <motion.div
                    className={`absolute inset-0 bg-gradient-to-r ${gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-300 pointer-events-none`}
                  />
                </motion.div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
