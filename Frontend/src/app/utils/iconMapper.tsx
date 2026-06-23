/**
 * Icon mapper utility
 * Maps icon name strings to Lucide React icons
 */
import {
  Github,
  Linkedin,
  Mail,
  Code2,
  Server,
  Cloud,
  Database,
  Terminal,
  Rocket,
  Award,
  Briefcase,
  ExternalLink,
  Smartphone,
  ShoppingCart,
  BarChart3,
  Workflow,
  Globe,
  Twitter,
  Phone,
  MapPin,
  Send,
  Calendar,
  Clock,
  Tag,
  ArrowRight,
  Heart,
} from "lucide-react";
import { LucideIcon } from "lucide-react";
import React from "react";

// Custom Instagram icon component (Lucide doesn't have Instagram)
// This matches the Lucide icon signature
const InstagramIcon = React.forwardRef<
  SVGSVGElement,
  React.ComponentProps<LucideIcon>
>(({ className, size, width, height, ...props }, ref) => {
  // Handle size prop (Lucide icons use size for both width and height)
  const iconSize = size || width || height || 24;
  return (
    <svg
      ref={ref}
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      width={iconSize}
      height={iconSize}
      className={className}
      {...props}
    >
      <rect width="20" height="20" x="2" y="2" rx="5" ry="5" />
      <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z" />
      <line x1="17.5" y1="6.5" x2="17.51" y2="6.5" />
    </svg>
  );
}) as LucideIcon;
InstagramIcon.displayName = "Instagram";

const iconMap: Record<string, LucideIcon> = {
  Github,
  Linkedin,
  Mail,
  Code2,
  Server,
  Cloud,
  Database,
  Terminal,
  Rocket,
  Award,
  Briefcase,
  ExternalLink,
  Smartphone,
  ShoppingCart,
  BarChart3,
  Workflow,
  Globe,
  Twitter,
  Instagram: InstagramIcon,
  Phone,
  MapPin,
  Send,
  Calendar,
  Clock,
  Tag,
  ArrowRight,
  Heart,
};

// Platform name to icon name mapping (case-insensitive)
const platformIconMap: Record<string, string> = {
  github: "Github",
  linkedin: "Linkedin",
  instagram: "Instagram",
  twitter: "Twitter",
  mail: "Mail",
  email: "Mail",
  phone: "Phone",
  globe: "Globe",
};

export function getIcon(iconName: string | null, platformName?: string | null): LucideIcon | null {
  if (!iconName && !platformName) return null;
  
  // First try iconName directly
  if (iconName) {
    const icon = iconMap[iconName];
    if (icon) return icon;
  }
  
  // If iconName doesn't work, try to map from platform name
  if (platformName) {
    const mappedIconName = platformIconMap[platformName.toLowerCase()];
    if (mappedIconName) {
      const icon = iconMap[mappedIconName];
      if (icon) return icon;
    }
  }
  
  return null;
}

export function getIconOrDefault(
  iconName: string | null,
  defaultIcon: LucideIcon,
  platformName?: string | null
): LucideIcon {
  return getIcon(iconName, platformName) || defaultIcon;
}
