// Native HTML5 Canvas Confetti - Lightweight, zero-dependency, zero-cost celebration
export function triggerConfetti() {
  if (typeof window === 'undefined') return;

  const canvas = document.createElement('canvas');
  canvas.style.position = 'fixed';
  canvas.style.top = '0';
  canvas.style.left = '0';
  canvas.style.width = '100vw';
  canvas.style.height = '100vh';
  canvas.style.pointerEvents = 'none';
  canvas.style.zIndex = '999999';
  document.body.appendChild(canvas);

  const ctx = canvas.getContext('2d');
  if (!ctx) {
    canvas.remove();
    return;
  }

  const dpr = window.devicePixelRatio || 1;
  const width = window.innerWidth;
  const height = window.innerHeight;
  canvas.width = width * dpr;
  canvas.height = height * dpr;
  ctx.scale(dpr, dpr);

  const colors = ['#10b981', '#059669', '#3b82f6', '#f59e0b', '#ec4899', '#8b5cf6', '#ef4444'];
  const particleCount = 100;
  const particles: Array<{
    x: number;
    y: number;
    vx: number;
    vy: number;
    color: string;
    size: number;
    rotation: number;
    vRotation: number;
    opacity: number;
  }> = [];

  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: width * 0.5 + (Math.random() - 0.5) * 200,
      y: height * 0.4 + (Math.random() - 0.5) * 100,
      vx: (Math.random() - 0.5) * 14,
      vy: Math.random() * -12 - 4,
      color: colors[Math.floor(Math.random() * colors.length)],
      size: Math.random() * 8 + 4,
      rotation: Math.random() * 360,
      vRotation: (Math.random() - 0.5) * 12,
      opacity: 1
    });
  }

  let animationFrameId: number;
  const startTime = Date.now();
  const duration = 2500;

  function render() {
    const elapsed = Date.now() - startTime;
    if (elapsed > duration || !ctx) {
      cancelAnimationFrame(animationFrameId);
      canvas.remove();
      return;
    }

    ctx.clearRect(0, 0, width, height);

    for (const p of particles) {
      p.x += p.vx;
      p.y += p.vy;
      p.vy += 0.35; // gravity
      p.vx *= 0.98; // air resistance
      p.rotation += p.vRotation;
      p.opacity = Math.max(0, 1 - elapsed / duration);

      ctx.save();
      ctx.translate(p.x, p.y);
      ctx.rotate((p.rotation * Math.PI) / 180);
      ctx.globalAlpha = p.opacity;
      ctx.fillStyle = p.color;
      ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.6);
      ctx.restore();
    }

    animationFrameId = requestAnimationFrame(render);
  }

  render();
}
