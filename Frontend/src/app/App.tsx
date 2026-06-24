import React, { useCallback, useEffect, useRef, useState } from "react";
import { BrowserRouter, Routes, Route, useLocation } from "react-router";
import { Navigation } from "./components/navigation";
import { HeroSection } from "./components/hero-section";
import { AboutSection } from "./components/about-section";
import { ProjectsSection } from "./components/projects-section";
import { BlogSection } from "./components/blog-section";
import { ContactSection } from "./components/contact-section";
import { Footer } from "./components/footer";
import { LandingLoader } from "./components/landing-loader";
import { BlogListPage } from "./pages/blog-list-page";
import { NotFoundPage } from "./pages/not-found-page";
import { ErrorPage } from "./pages/error-page";

function HomePage() {
  const location = useLocation();
  const scrollTo = (location.state as { scrollTo?: string })?.scrollTo;
  const siteRef = useRef<HTMLDivElement>(null);
  const [loaderDone, setLoaderDone] = useState(false);
  const handleLoaderComplete = useCallback(() => setLoaderDone(true), []);

  useEffect(() => {
    if (scrollTo) {
      let intervalId: ReturnType<typeof setInterval> | null = null;
      let scrollTimeout: ReturnType<typeof setTimeout> | null = null;
      
      // Function to perform scroll
      const performScroll = () => {
        if (scrollTo === "home") {
          window.scrollTo({ top: 0, behavior: "smooth" });
          return true;
        } else {
          const element = document.getElementById(scrollTo);
          if (element) {
            // Calculate position with offset for fixed navbar
            const offset = 80;
            const elementTop = element.getBoundingClientRect().top;
            const elementPosition = elementTop + window.pageYOffset;
            const offsetPosition = elementPosition - offset;
            
            // Scroll to the calculated position
            window.scrollTo({
              top: Math.max(0, offsetPosition),
              behavior: "smooth",
            });
            
            // Double-check after a short delay and adjust if needed
            if (scrollTimeout) {
              clearTimeout(scrollTimeout);
            }
            scrollTimeout = setTimeout(() => {
              const finalElement = document.getElementById(scrollTo);
              if (finalElement) {
                const finalTop = finalElement.getBoundingClientRect().top;
                if (Math.abs(finalTop - offset) > 10) {
                  // If not at correct position, adjust
                  window.scrollBy({
                    top: finalTop - offset,
                    behavior: "smooth",
                  });
                }
              }
            }, 500);
            
            return true;
          }
        }
        return false;
      };

      // Wait for page to render, then try scrolling
      const initialDelay = setTimeout(() => {
        // Try to scroll immediately
        if (performScroll()) {
          return;
        }

        // If element not found, wait and retry with polling
        let attempts = 0;
        const maxAttempts = 50; // Try for up to 5 seconds (50 * 100ms)
        
        intervalId = setInterval(() => {
          attempts++;
          if (performScroll() || attempts >= maxAttempts) {
            if (intervalId) {
              clearInterval(intervalId);
              intervalId = null;
            }
          }
        }, 100);
      }, 400); // Initial delay to let page start rendering

      return () => {
        clearTimeout(initialDelay);
        if (intervalId) {
          clearInterval(intervalId);
        }
        if (scrollTimeout) {
          clearTimeout(scrollTimeout);
        }
      };
    }
  }, [scrollTo, location.pathname]);

  return (
    <>
      {!loaderDone && (
        <LandingLoader siteRef={siteRef} onComplete={handleLoaderComplete} />
      )}
      <div ref={siteRef} className="landing-site min-h-screen bg-slate-950 text-white overflow-x-hidden">
        <div data-landing-reveal>
          <Navigation />
        </div>
        <main>
          <div data-landing-reveal>
            <HeroSection />
          </div>
          <AboutSection />
          <ProjectsSection />
          <BlogSection />
          <ContactSection />
        </main>
        <Footer />
      </div>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/blog" element={<BlogListPage />} />
        <Route path="/500" element={<ErrorPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}
