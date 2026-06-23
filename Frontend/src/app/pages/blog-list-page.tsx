import React, { useState, useEffect } from "react";
import { motion } from "motion/react";
import { useNavigate } from "react-router";
import { ArrowLeft, Calendar, Clock, Tag } from "lucide-react";
import { Card } from "../components/ui/card";
import { api, BlogPost } from "../services/api";
import { Navigation } from "../components/navigation";
import { Footer } from "../components/footer";

export function BlogListPage() {
  const navigate = useNavigate();
  const [blogPosts, setBlogPosts] = useState<BlogPost[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBlogPosts = async () => {
      try {
        // Fetch all published posts
        const allPostsData = await api.getBlogPostsWithInfo(false, 100);
        const allPosts = allPostsData.posts;
        
        // Filter only published posts (is_published=true)
        const publishedPosts = allPosts.filter((post: BlogPost) => {
          return post.is_published === true;
        });
        
        // Sort by date (newest first)
        const sortedPosts = publishedPosts.sort((a: BlogPost, b: BlogPost) => {
          return new Date(b.date).getTime() - new Date(a.date).getTime();
        });
        
        setBlogPosts(sortedPosts);
      } catch (error) {
        console.error("Failed to fetch blog posts:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchBlogPosts();
  }, []);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-white">
        <Navigation />
        <div className="container mx-auto px-6 py-20">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-500"></div>
            <p className="mt-4 text-slate-400">Loading blog posts...</p>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <Navigation />
      <main>
        {/* Header Section */}
        <section className="pt-32 pb-20 bg-gradient-to-b from-slate-950 via-purple-950/20 to-slate-950 relative overflow-hidden">
          <div className="absolute inset-0 bg-[linear-gradient(rgba(168,85,247,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(168,85,247,0.03)_1px,transparent_1px)] bg-[size:50px_50px]"></div>
          <div className="container mx-auto px-6 relative z-10">
            {/* Back Button */}
            <motion.button
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              onClick={() => navigate("/")}
              className="flex items-center gap-2 text-slate-400 hover:text-cyan-400 transition-colors mb-8 group"
            >
              <ArrowLeft size={20} className="group-hover:-translate-x-1 transition-transform" />
              <span>Back to Home</span>
            </motion.button>

            {/* Title */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="text-center mb-16"
            >
              <h1 className="text-5xl md:text-6xl mb-4 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                All Blog Posts
              </h1>
              <p className="text-xl text-slate-400 max-w-2xl mx-auto">
                {blogPosts.length} {blogPosts.length === 1 ? "post" : "posts"} published
              </p>
            </motion.div>
          </div>
        </section>

        {/* Blog Posts Grid */}
        <section className="py-20 bg-gradient-to-b from-slate-950 via-purple-950/20 to-slate-950 relative overflow-hidden">
          <div className="absolute inset-0 bg-[linear-gradient(rgba(168,85,247,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(168,85,247,0.03)_1px,transparent_1px)] bg-[size:50px_50px]"></div>
          <div className="container mx-auto px-6 relative z-10">
            {blogPosts.length === 0 ? (
              <div className="text-center py-20">
                <p className="text-xl text-slate-400">No blog posts available.</p>
              </div>
            ) : (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
                {blogPosts.map((post, index) => (
                  <motion.div
                    key={post.id}
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                  >
                    <a href="#" className="block h-full">
                      <Card className="text-card-foreground flex flex-col gap-6 rounded-xl border h-full bg-slate-800/50 backdrop-blur-sm border-slate-700 hover:border-purple-500/50 transition-all duration-300 overflow-hidden group">
                        {/* Image */}
                        <div className="relative h-48 overflow-hidden">
                          <img
                            src={post.image_url || "https://images.unsplash.com/photo-1667372393119-3d4c48d07fc9?w=1200&h=600&fit=crop"}
                            alt={post.title}
                            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                          />
                          <div className="absolute inset-0 bg-gradient-to-t from-slate-900 to-transparent"></div>
                          {post.category && (
                            <div className="absolute top-4 left-4">
                              <span className="px-3 py-1 bg-purple-500/80 backdrop-blur-sm text-white text-xs rounded-full">
                                {post.category}
                              </span>
                            </div>
                          )}
                          {post.is_featured && (
                            <div className="absolute top-4 right-4">
                              <span className="px-3 py-1 bg-cyan-500/80 backdrop-blur-sm text-white text-xs rounded-full">
                                Featured
                              </span>
                            </div>
                          )}
                        </div>

                        {/* Content */}
                        <div className="p-6 flex-1 flex flex-col">
                          <h3 className="text-xl text-white mb-3 group-hover:text-purple-400 transition-colors line-clamp-2">
                            {post.title}
                          </h3>
                          <p className="text-slate-400 mb-4 line-clamp-3 text-sm flex-1">
                            {post.excerpt}
                          </p>

                          {/* Meta Info */}
                          <div className="flex flex-wrap items-center gap-4 text-slate-500 text-xs mt-auto pt-4 border-t border-slate-700">
                            <div className="flex items-center gap-1">
                              <Calendar size={14} className="text-cyan-400" />
                              <span>{formatDate(post.date)}</span>
                            </div>
                            {post.read_time && (
                              <div className="flex items-center gap-1">
                                <Clock size={14} className="text-cyan-400" />
                                <span>{post.read_time}</span>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Hover Overlay */}
                        <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
                      </Card>
                    </a>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
