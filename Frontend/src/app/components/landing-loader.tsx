import { useEffect, useRef } from "react";
import * as THREE from "three";
import gsap from "gsap";
import "./landing-loader.css";

const STATUSES = [
  "Initializing reality…",
  "Calibrating particles…",
  "Weaving dimensions…",
  "Syncing neural mesh…",
  "Almost there…",
];

const COUNT = 6000;

type LandingLoaderProps = {
  siteRef: React.RefObject<HTMLElement | null>;
  onComplete: () => void;
};

export function LandingLoader({ siteRef, onComplete }: LandingLoaderProps) {
  const loaderRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const counterRef = useRef<HTMLSpanElement>(null);
  const statusRef = useRef<HTMLParagraphElement>(null);
  const barFillRef = useRef<HTMLDivElement>(null);
  const uiRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reducedMotion) {
      document.body.classList.add("landing-ready");
      const site = siteRef.current;
      if (site) {
        site.style.opacity = "1";
        site.style.visibility = "visible";
      }
      onComplete();
      return;
    }

    const loader = loaderRef.current;
    const canvas = canvasRef.current;
    const counterEl = counterRef.current;
    const statusEl = statusRef.current;
    const barFill = barFillRef.current;
    const uiEl = uiRef.current;
    const siteRoot = siteRef.current;

    if (!loader || !canvas || !counterEl || !statusEl || !barFill || !uiEl || !siteRoot) {
      return;
    }

    const revealTargets = siteRoot.querySelectorAll("[data-landing-reveal]");
    const loaderEl: HTMLDivElement = loader;
    const counterNode: HTMLSpanElement = counterEl;
    const statusNode: HTMLParagraphElement = statusEl;
    const barFillNode: HTMLDivElement = barFill;
    const uiRoot: HTMLDivElement = uiEl;

    document.body.classList.add("landing-loading");

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 100);
    camera.position.z = 4.2;

    const renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: true,
      powerPreference: "high-performance",
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x050508, 1);

    const positions = new Float32Array(COUNT * 3);

    for (let i = 0; i < COUNT; i++) {
      const i3 = i * 3;
      positions[i3] = (Math.random() - 0.5) * 8;
      positions[i3 + 1] = (Math.random() - 0.5) * 8;
      positions[i3 + 2] = (Math.random() - 0.5) * 8;
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));

    const material = new THREE.PointsMaterial({
      size: 0.028,
      color: 0x7cf4c4,
      transparent: true,
      opacity: 0.85,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      sizeAttenuation: true,
    });

    const particles = new THREE.Points(geometry, material);
    scene.add(particles);

    function fillSphere(arr: Float32Array, radius: number) {
      for (let i = 0; i < COUNT; i++) {
        const i3 = i * 3;
        const phi = Math.acos(2 * Math.random() - 1);
        const theta = Math.random() * Math.PI * 2;
        const r = radius * (0.85 + Math.random() * 0.15);
        arr[i3] = r * Math.sin(phi) * Math.cos(theta);
        arr[i3 + 1] = r * Math.sin(phi) * Math.sin(theta);
        arr[i3 + 2] = r * Math.cos(phi);
      }
    }

    function fillTorus(arr: Float32Array, R: number, r: number) {
      for (let i = 0; i < COUNT; i++) {
        const i3 = i * 3;
        const u = Math.random() * Math.PI * 2;
        const v = Math.random() * Math.PI * 2;
        arr[i3] = (R + r * Math.cos(v)) * Math.cos(u);
        arr[i3 + 1] = (R + r * Math.cos(v)) * Math.sin(u);
        arr[i3 + 2] = r * Math.sin(v);
      }
    }

    function fillHelix(arr: Float32Array) {
      for (let i = 0; i < COUNT; i++) {
        const i3 = i * 3;
        const t = (i / COUNT) * Math.PI * 10;
        const rad = 1.2 + Math.random() * 0.3;
        arr[i3] = Math.cos(t) * rad;
        arr[i3 + 1] = (i / COUNT - 0.5) * 5;
        arr[i3 + 2] = Math.sin(t) * rad;
      }
    }

    const shapeA = new Float32Array(COUNT * 3);
    const shapeB = new Float32Array(COUNT * 3);
    const shapeC = new Float32Array(COUNT * 3);
    fillSphere(shapeA, 1.8);
    fillTorus(shapeB, 1.4, 0.55);
    fillHelix(shapeC);

    let mouseX = 0;
    let mouseY = 0;
    let progress = 0;
    let loadDone = false;
    let exiting = false;
    let frameId = 0;

    function resize() {
      const w = window.innerWidth;
      const h = window.innerHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    }

    resize();

    const onResize = () => resize();
    const onMouseMove = (e: MouseEvent) => {
      mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
      mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
    };

    window.addEventListener("resize", onResize);
    document.addEventListener("mousemove", onMouseMove);

    function lerpShapes(t: number) {
      const pos = geometry.attributes.position.array as Float32Array;
      let from: Float32Array;
      let to: Float32Array;
      let mix: number;

      if (t < 0.4) {
        from = shapeA;
        to = shapeB;
        mix = t / 0.4;
      } else if (t < 0.75) {
        from = shapeB;
        to = shapeC;
        mix = (t - 0.4) / 0.35;
      } else {
        from = shapeC;
        to = shapeA;
        mix = (t - 0.75) / 0.25;
      }

      const ease =
        mix < 0.5 ? 4 * mix * mix * mix : 1 - Math.pow(-2 * mix + 2, 3) / 2;

      for (let i = 0; i < COUNT * 3; i++) {
        pos[i] = from[i] + (to[i] - from[i]) * ease;
      }
      geometry.attributes.position.needsUpdate = true;
    }

    function animate() {
      frameId = requestAnimationFrame(animate);

      const t = performance.now() * 0.001;
      particles.rotation.y = t * 0.15 + mouseX * 0.3;
      particles.rotation.x = mouseY * 0.2;

      if (!exiting) {
        lerpShapes(progress / 100);
        material.opacity = 0.5 + (progress / 100) * 0.45;
        camera.position.z = 4.2 - (progress / 100) * 0.8;
      } else {
        particles.rotation.y += 0.04;
        material.opacity *= 0.96;
      }

      camera.position.x += (mouseX * 0.4 - camera.position.x) * 0.04;
      camera.position.y += (-mouseY * 0.3 - camera.position.y) * 0.04;
      camera.lookAt(0, 0, 0);

      renderer.render(scene, camera);
    }

    animate();

    let loadTimeline: gsap.core.Timeline | null = null;
    let exitTimeline: gsap.core.Timeline | null = null;
    let introAnimation: gsap.core.Animation | null = null;

    function exitLoader() {
      if (loadDone) return;
      loadDone = true;
      exiting = true;

      exitTimeline = gsap.timeline({
        onComplete: () => {
          cancelAnimationFrame(frameId);
          renderer.dispose();
          geometry.dispose();
          material.dispose();
          document.body.classList.remove("landing-loading");
          document.body.classList.add("landing-ready");
          onComplete();
        },
      });

      exitTimeline
        .to(camera.position, { z: 0.5, duration: 1.1, ease: "power3.in" }, 0)
        .to(material, { opacity: 0, duration: 0.8 }, 0.2)
        .to(
          loaderEl,
          {
            opacity: 0,
            scale: 1.06,
            duration: 0.9,
            ease: "power3.inOut",
          },
          0.35,
        )
        .to(
          siteRoot,
          {
            opacity: 1,
            visibility: "visible",
            duration: 1,
            ease: "power2.out",
          },
          0.6,
        )
        .from(
          revealTargets,
          {
            y: 40,
            opacity: 0,
            duration: 0.9,
            stagger: 0.12,
            ease: "power3.out",
          },
          0.75,
        );
    }

    function runLoad() {
      const obj = { value: 0 };
      let statusIdx = 0;

      loadTimeline = gsap.timeline({
        onComplete: exitLoader,
      });

      loadTimeline.to(obj, {
        value: 100,
        duration: 3.2,
        ease: "power2.inOut",
        onUpdate: () => {
          const v = Math.round(obj.value);
          progress = obj.value;
          counterNode.textContent = String(v).padStart(3, "0");
          barFillNode.style.width = `${v}%`;

          const nextStatus = Math.floor(obj.value / 22);
          if (nextStatus !== statusIdx && nextStatus < STATUSES.length) {
            statusIdx = nextStatus;
            gsap.fromTo(
              statusNode,
              { opacity: 0, y: 6 },
              { opacity: 1, y: 0, duration: 0.4 },
            );
            statusNode.textContent = STATUSES[statusIdx];
          }
        },
      });
    }

    document.fonts.ready.then(() => {
      introAnimation = gsap.from(uiRoot.children, {
        y: 24,
        opacity: 0,
        duration: 0.9,
        stagger: 0.1,
        ease: "power3.out",
        onComplete: runLoad,
      });
    });

    return () => {
      cancelAnimationFrame(frameId);
      window.removeEventListener("resize", onResize);
      document.removeEventListener("mousemove", onMouseMove);
      loadTimeline?.kill();
      exitTimeline?.kill();
      introAnimation?.kill();
      renderer.dispose();
      geometry.dispose();
      material.dispose();
      document.body.classList.remove("landing-loading", "landing-ready");
    };
  }, [onComplete, siteRef]);

  return (
    <div className="landing-loader" ref={loaderRef} aria-hidden="false">
      <canvas ref={canvasRef} className="landing-loader__canvas" />
      <div className="landing-loader__vignette" aria-hidden="true" />

      <div className="landing-loader__ui" ref={uiRef}>
        <div className="landing-loader__brand">
          <span className="landing-loader__brand-dot" />
          <span className="landing-loader__brand-text">CAN KARTAL</span>
        </div>
        <div className="landing-loader__counter">
          <span ref={counterRef}>000</span>
          <span className="landing-loader__counter-unit">%</span>
        </div>
        <p className="landing-loader__status" ref={statusRef}>
          Initializing reality…
        </p>
        <div className="landing-loader__bar">
          <div className="landing-loader__bar-fill" ref={barFillRef} />
        </div>
      </div>
    </div>
  );
}
