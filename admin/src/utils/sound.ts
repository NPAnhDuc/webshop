// Web Audio API Synthesizer for optional subtle feedback
// Default to muted for clean, professional e-commerce experience

class SoundManager {
  private ctx: AudioContext | null = null;
  private isMuted: boolean = true;

  constructor() {
    // Default muted so it doesn't feel like an arcade game
    const saved = localStorage.getItem('techstore_sound_muted');
    if (saved !== null) {
      this.isMuted = saved === 'true';
    } else {
      this.isMuted = true;
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

  public playCartAdd() {
    if (this.isMuted) return;
    this.initContext();
    if (!this.ctx) return;

    const now = this.ctx.currentTime;
    this.playTone(523.25, now, 0.08, 0.06);
    this.playTone(659.25, now + 0.07, 0.1, 0.08);
  }

  public playPop() {
    if (this.isMuted) return;
    this.initContext();
    if (!this.ctx) return;

    const now = this.ctx.currentTime;
    this.playTone(880, now, 0.04, 0.08, 'sine');
  }

  public playVoucherSuccess() {
    if (this.isMuted) return;
    this.initContext();
    if (!this.ctx) return;

    const now = this.ctx.currentTime;
    this.playTone(523.25, now, 0.06, 0.06);
    this.playTone(659.25, now + 0.06, 0.06, 0.06);
    this.playTone(783.99, now + 0.12, 0.06, 0.06);
    this.playTone(1046.50, now + 0.18, 0.15, 0.08);
  }

  public playClick() {
    if (this.isMuted) return;
    this.initContext();
    if (!this.ctx) return;

    const now = this.ctx.currentTime;
    this.playTone(440, now, 0.02, 0.03, 'triangle');
  }

  private playTone(freq: number, startTime: number, duration: number, volume: number = 0.05, type: OscillatorType = 'sine') {
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
    this.playTone(freq, this.ctx.currentTime, duration, 0.05, type);
  }
}

export const sound = new SoundManager();
