// Web Audio API Synthesizer for subtle, high-class tactile audio feedback
// Zero external files, zero latency, works offline

class SoundManager {
  private ctx: AudioContext | null = null;
  private isMuted: boolean = false;

  constructor() {
    // Load mute preference from localStorage
    const saved = localStorage.getItem('techstore_sound_muted');
    if (saved !== null) {
      this.isMuted = saved === 'true';
    }
  }

  private initContext() {
    if (!this.ctx && typeof window !== 'undefined') {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  public toggleMute(): boolean {
    this.isMuted = !this.isMuted;
    localStorage.setItem('techstore_sound_muted', String(this.isMuted));
    if (!this.isMuted) {
      this.playChime(659.25, 0.08, 'sine');
    }
    return this.isMuted;
  }

  public getIsMuted(): boolean {
    return this.isMuted;
  }

  // Sweet gentle chime when adding item to cart
  public playCartAdd() {
    if (this.isMuted) return;
    this.initContext();
    if (!this.ctx) return;

    const now = this.ctx.currentTime;
    // Two-tone rising major third (C5 -> E5)
    this.playTone(523.25, now, 0.08, 0.12);
    this.playTone(659.25, now + 0.07, 0.14, 0.15);
  }

  // Pop sound for heart / wishlist toggle
  public playPop() {
    if (this.isMuted) return;
    this.initContext();
    if (!this.ctx) return;

    const now = this.ctx.currentTime;
    this.playTone(880, now, 0.05, 0.15, 'sine');
  }

  // Celebratory fanfare chime for coupon success
  public playVoucherSuccess() {
    if (this.isMuted) return;
    this.initContext();
    if (!this.ctx) return;

    const now = this.ctx.currentTime;
    // C5 -> E5 -> G5 -> C6
    this.playTone(523.25, now, 0.08, 0.1);
    this.playTone(659.25, now + 0.08, 0.08, 0.1);
    this.playTone(783.99, now + 0.16, 0.08, 0.1);
    this.playTone(1046.50, now + 0.24, 0.25, 0.15);
  }

  // Subtle click for tabs and toggles
  public playClick() {
    if (this.isMuted) return;
    this.initContext();
    if (!this.ctx) return;

    const now = this.ctx.currentTime;
    this.playTone(440, now, 0.02, 0.04, 'triangle');
  }

  private playTone(freq: number, startTime: number, duration: number, volume: number = 0.1, type: OscillatorType = 'sine') {
    if (!this.ctx) return;
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = type;
      osc.frequency.setValueAtTime(freq, startTime);

      gain.gain.setValueAtTime(volume, startTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, startTime + duration);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(startTime);
      osc.stop(startTime + duration);
    } catch {
      // Audio autoplay policy fallback
    }
  }

  private playChime(freq: number, duration: number, type: OscillatorType) {
    this.initContext();
    if (!this.ctx) return;
    this.playTone(freq, this.ctx.currentTime, duration, 0.08, type);
  }
}

export const sound = new SoundManager();
