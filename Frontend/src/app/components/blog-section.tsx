import React from "react";
import { motion, useInView } from "motion/react";
import { useRef, useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { ArrowRight, Calendar, Clock, Tag } from "lucide-react";
import { Card } from "./ui/card";
import { api, BlogPost } from "../services/api";

export function BlogSection() {
  const navigate = useNavigate();
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, amount: 0.1 });
  const [hoveredId, setHoveredId] = useState<number | null>(null);
  const [featuredPost, setFeaturedPost] = useState<BlogPost | null>(null);
  const [blogPosts, setBlogPosts] = useState<BlogPost[]>([]);
  const [totalPosts, setTotalPosts] = useState<number>(0);
  const [displayedPostsCount, setDisplayedPostsCount] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [dataLoaded, setDataLoaded] = useState(false);

  useEffect(() => {
    const fetchBlogPosts = async () => {
      try {
        // Fetch all published posts with pagination info
        const allPostsData = await api.getBlogPostsWithInfo(false, 100);
        const allPosts = allPostsData.posts;
        
        // Fetch featured posts
        const featuredData = await api.getBlogPostsWithInfo(true, 100);
        const featured = featuredData.posts;
        
        // Filter only published posts (is_published=true)
        // Backend already filters, but we add extra safety check
        const publishedFeatured = featured.filter((post: BlogPost) => {
          // Only include posts with is_published explicitly set to true
          return post.is_published === true;
        });
        const publishedAll = allPosts.filter((post: BlogPost) => {
          // Only include posts with is_published explicitly set to true
          return post.is_published === true;
        });
        
        // Set total count from filtered published posts
        setTotalPosts(publishedAll.length);
        
        // Get first featured post
        const featuredItem = publishedFeatured.length > 0 ? publishedFeatured[0] : null;
        setFeaturedPost(featuredItem);
        
        // Get non-featured posts (limit to 6 for display)
        const nonFeatured = publishedAll.filter(post => !post.is_featured || post.id !== featuredItem?.id).slice(0, 6);
        setBlogPosts(nonFeatured);
        
        // Calculate displayed posts count (featured + non-featured)
        const displayedCount = (featuredItem ? 1 : 0) + nonFeatured.length;
        setDisplayedPostsCount(displayedCount);
        setDataLoaded(true);
      } catch (error) {
        console.error("Failed to fetch blog posts:", error);
        setDataLoaded(true);
      } finally {
        setLoading(false);
      }
    };

    fetchBlogPosts();
  }, []);

  const formatDate = (dateString: string) => {
    if (!dateString) return "";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
  };

  // Don't render section if there are no published blog posts
  const hasPublishedPosts = featuredPost !== null || blogPosts.length > 0;
  
  if (loading) {
    return null;
  }

  if (!hasPublishedPosts) {
    return null;
  }

  return (
    <section
      id="blog"
      ref={ref}
      className="min-h-screen py-20 bg-gradient-to-b from-slate-950 via-purple-950/20 to-slate-950 relative overflow-hidden"
    >
      {/* Background decoration */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(168,85,247,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(168,85,247,0.03)_1px,transparent_1px)] bg-[size:50px_50px]" />

      <div className="container mx-auto px-6 relative z-10">
        {/* Section Title */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={dataLoaded ? (isInView ? { opacity: 1, y: 0 } : { opacity: 1, y: 0 }) : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl md:text-6xl mb-4 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
            Latest Insights
          </h2>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto">
            Thoughts on development, cloud architecture, and engineering culture
          </p>
        </motion.div>

        {/* Featured Post */}
        {featuredPost && (
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={dataLoaded ? (isInView ? { opacity: 1, y: 0 } : { opacity: 1, y: 0 }) : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="max-w-6xl mx-auto mb-16"
          >
            <motion.a
              href={featuredPost.url || "#"}
              target={featuredPost.url && (featuredPost.url.startsWith("http://") || featuredPost.url.startsWith("https://")) ? "_blank" : undefined}
              rel={featuredPost.url && (featuredPost.url.startsWith("http://") || featuredPost.url.startsWith("https://")) ? "noopener noreferrer" : undefined}
              onClick={(e) => {
                if (!featuredPost.url) {
                  e.preventDefault();
                }
              }}
              whileHover={{ y: -10 }}
              transition={{ type: "spring", stiffness: 300 }}
              onMouseEnter={() => setHoveredId(featuredPost.id)}
              onMouseLeave={() => setHoveredId(null)}
              className="relative bg-slate-800/50 backdrop-blur-sm rounded-2xl overflow-hidden border border-cyan-500/30 hover:border-cyan-500 transition-all duration-300 group block"
            >
              <div className="grid lg:grid-cols-2 gap-0">
                {/* Image */}
                <div className="relative h-64 lg:h-auto overflow-hidden">
                  <motion.img
                    src={featuredPost.image_url || "https://images.unsplash.com/photo-1667372393119-3d4c48d07fc9?w=1200&h=600&fit=crop"}
                    alt={featuredPost.title}
                    className="w-full h-full object-cover"
                    animate={{
                      scale: hoveredId === featuredPost.id ? 1.1 : 1,
                    }}
                    transition={{ duration: 0.4 }}
                  />
                  <div className="absolute inset-0 bg-gradient-to-r from-slate-900/50 to-transparent" />
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{
                      opacity: hoveredId === featuredPost.id ? 1 : 0,
                    }}
                    className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-purple-500/20"
                  />
                </div>

                {/* Content */}
                <div className="p-8 lg:p-12 flex flex-col justify-center">
                  <div className="mb-4">
                    <span className="px-4 py-1.5 bg-gradient-to-r from-cyan-500 to-purple-500 text-white text-sm rounded-full">
                      Featured Post
                    </span>
                  </div>
                  <h3 className="text-3xl lg:text-4xl text-white mb-4 group-hover:text-cyan-400 transition-colors">
                    {featuredPost.title}
                  </h3>
                  <p className="text-slate-300 mb-6 text-lg">
                    {featuredPost.excerpt}
                  </p>

                  {/* Meta Info */}
                  <div className="flex flex-wrap gap-4 text-slate-400 mb-6">
                    <div className="flex items-center gap-2">
                      <Calendar size={16} className="text-cyan-400" />
                      <span className="text-sm">{formatDate(featuredPost.date)}</span>
                    </div>
                    {featuredPost.read_time && (
                      <div className="flex items-center gap-2">
                        <Clock size={16} className="text-cyan-400" />
                        <span className="text-sm">{featuredPost.read_time}</span>
                      </div>
                    )}
                    {featuredPost.category && (
                      <div className="flex items-center gap-2">
                        <Tag size={16} className="text-cyan-400" />
                        <span className="text-sm">{featuredPost.category}</span>
                      </div>
                    )}
                  </div>

                  {/* Read More Button */}
                  <motion.span
                    whileHover={{ x: 5 }}
                    className="flex items-center gap-2 text-cyan-400 hover:text-cyan-300 transition-colors group/link w-fit cursor-pointer"
                  >
                    <span className="text-lg">Read More</span>
                    <ArrowRight
                      size={20}
                      className="group-hover/link:translate-x-1 transition-transform"
                    />
                  </motion.span>
                </div>
              </div>
            </motion.a>
          </motion.div>
        )}

        {/* Blog Posts Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
          {blogPosts.map((post, index) => (
            <motion.div
              key={post.id}
              initial={{ opacity: 0, y: 50 }}
              animate={dataLoaded ? (isInView ? { opacity: 1, y: 0 } : { opacity: 1, y: 0 }) : {}}
              transition={{ duration: 0.6, delay: 0.4 + index * 0.1 }}
              onMouseEnter={() => setHoveredId(post.id)}
              onMouseLeave={() => setHoveredId(null)}
            >
              <motion.a
                href={post.url || "#"}
                target={post.url && (post.url.startsWith("http://") || post.url.startsWith("https://")) ? "_blank" : undefined}
                rel={post.url && (post.url.startsWith("http://") || post.url.startsWith("https://")) ? "noopener noreferrer" : undefined}
                onClick={(e) => {
                  if (!post.url) {
                    e.preventDefault();
                  }
                }}
                whileHover={{ y: -10 }}
                transition={{ type: "spring", stiffness: 300 }}
                className="block h-full"
              >
                <Card className="h-full bg-slate-800/50 backdrop-blur-sm border-slate-700 hover:border-purple-500/50 transition-all duration-300 overflow-hidden group">
                  {/* Image */}
                  {post.image_url && (
                    <div className="relative h-48 overflow-hidden">
                      <motion.img
                        src={post.image_url}
                        alt={post.title}
                        className="w-full h-full object-cover"
                        animate={{
                          scale: hoveredId === post.id ? 1.1 : 1,
                        }}
                        transition={{ duration: 0.4 }}
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-slate-900 to-transparent" />
                    
                      {/* Category Badge */}
                      {post.category && (
                        <div className="absolute top-4 left-4">
                          <span className="px-3 py-1 bg-purple-500/80 backdrop-blur-sm text-white text-xs rounded-full">
                            {post.category}
                          </span>
                        </div>
                      )}
                    </div>
                  )}
                  
                  {/* Category Badge - Show when no image */}
                  {!post.image_url && post.category && (
                    <div className="absolute top-4 left-4">
                      <span className="px-3 py-1 bg-purple-500/80 backdrop-blur-sm text-white text-xs rounded-full">
                        {post.category}
                      </span>
                    </div>
                  )}

                  {/* Content */}
                  <div className="p-6">
                    <h3 className="text-xl text-white mb-3 group-hover:text-purple-400 transition-colors line-clamp-2">
                      {post.title}
                    </h3>
                    <p className="text-slate-400 mb-4 line-clamp-2 text-sm">
                      {post.excerpt}
                    </p>

                    {/* Meta */}
                    <div className="flex items-center gap-4 text-slate-500 text-xs">
                      <div className="flex items-center gap-1">
                        <Calendar size={14} />
                        <span>{formatDate(post.date)}</span>
                      </div>
                      {post.read_time && (
                        <div className="flex items-center gap-1">
                          <Clock size={14} />
                          <span>{post.read_time}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Hover Glow */}
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"
                  />
                </Card>
              </motion.a>
            </motion.div>
          ))}
        </div>

        {/* View All Button - Only show if there are 7 or more posts */}
        {totalPosts >= 7 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={dataLoaded ? (isInView ? { opacity: 1 } : { opacity: 1 }) : {}}
            transition={{ duration: 0.6, delay: 1 }}
            className="text-center mt-12"
          >
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate("/blog")}
              className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-cyan-500 to-purple-500 text-white rounded-full hover:shadow-lg hover:shadow-purple-500/50 transition-all"
            >
              <span>View All Posts ({totalPosts})</span>
              <ArrowRight size={20} />
            </motion.button>
          </motion.div>
        )}
      </div>
    </section>
  );
}
