import { Product } from '../types';

export interface PowerTelemetry {
  estimatedWattage: number;
  recommendedPsuWattage: number;
  selectedPsuWattage: number;
  headroomWattage: number;
  status: 'optimal' | 'adequate' | 'insufficient' | 'no_psu';
  statusMessage: string;
}

export interface GameTelemetry {
  id: string;
  name: string;
  genre: string;
  fps: number;
  fpsText: string;
  progressPct: number;
  experienceRating: 'ultra' | 'smooth' | 'playable' | 'laggy';
  badgeText: string;
  settingsNote: string;
}

export interface BottleneckAnalysis {
  bottleneckPct: number;
  dominantType: 'balanced' | 'cpu_bound' | 'gpu_bound' | 'no_gpu';
  title: string;
  summary: string;
  cpuScore: number;
  gpuScore: number;
  balanceScore: number; // 0 - 100%
}

export interface HardwarePerformanceReport {
  power: PowerTelemetry;
  bottleneck: BottleneckAnalysis;
  games: GameTelemetry[];
}

// 1. Power & Wattage Calculation
export function calculatePowerTelemetry(parts: Record<string, Product>): PowerTelemetry {
  let estimated = 70; // Base: Motherboard + Fans + RAM + M.2 SSD

  const cpu = parts['cpu'];
  const vga = parts['vga'];
  const psu = parts['psu'];
  const cooler = parts['cooler'];

  // CPU TDP
  if (cpu) {
    if (cpu.specs?.tdp_w) {
      estimated += cpu.specs.tdp_w;
    } else {
      const name = (cpu.name || '').toLowerCase();
      if (name.includes('i9') || name.includes('7950') || name.includes('9950') || name.includes('14900')) estimated += 220;
      else if (name.includes('i7') || name.includes('7800x3d') || name.includes('9800x3d') || name.includes('14700')) estimated += 160;
      else if (name.includes('i5') || name.includes('7600') || name.includes('9600') || name.includes('13600')) estimated += 105;
      else estimated += 65;
    }
  }

  // Cooler pump/fan power
  if (cooler) {
    const isAIO = (cooler.name || '').toLowerCase().includes('aio') || (cooler.name || '').toLowerCase().includes('nước');
    estimated += isAIO ? 25 : 10;
  }

  // VGA / GPU TGP
  if (vga) {
    if (vga.specs?.tgp_w) {
      estimated += vga.specs.tgp_w;
    } else {
      const name = (vga.name || '').toLowerCase();
      if (name.includes('4090') || name.includes('5090')) estimated += 450;
      else if (name.includes('4080') || name.includes('5080')) estimated += 320;
      else if (name.includes('4070 ti') || name.includes('7900')) estimated += 285;
      else if (name.includes('4070') || name.includes('7800')) estimated += 200;
      else if (name.includes('4060 ti') || name.includes('5060 ti')) estimated += 165;
      else if (name.includes('4060') || name.includes('5060') || name.includes('3060')) estimated += 130;
      else if (name.includes('3050') || name.includes('1650')) estimated += 85;
      else estimated += 120;
    }
  }

  const recommendedPsu = Math.ceil((estimated * 1.25) / 50) * 50;
  const selectedPsu = psu?.specs?.psu_watt || (psu ? parseInt(psu.name.match(/(\d{3,4})\s*w/i)?.[1] || '0', 10) : 0);

  let status: PowerTelemetry['status'] = 'no_psu';
  let statusMessage = 'Chưa chọn Nguồn máy tính (PSU). Cấu hình này cần tối thiểu ' + recommendedPsu + 'W.';
  const headroom = selectedPsu > 0 ? selectedPsu - estimated : 0;

  if (selectedPsu > 0) {
    if (selectedPsu < estimated) {
      status = 'insufficient';
      statusMessage = `CẢNH BÁO NGUY CƠ SẬP NGUỒN: Nguồn ${selectedPsu}W không đủ tải cho cấu hình ngốn ${estimated}W (Thiếu ${estimated - selectedPsu}W).`;
    } else if (selectedPsu < recommendedPsu) {
      status = 'adequate';
      statusMessage = `Nguồn ${selectedPsu}W đủ chạy cơ bản nhưng thiếu 25% công suất dự phòng khi tải nặng. Khuyến nghị nâng lên ${recommendedPsu}W.`;
    } else {
      status = 'optimal';
      statusMessage = `Công suất dồi dào (+${headroom}W dự phòng). Nguồn ${selectedPsu}W hoạt động êm ái ở điểm hiệu suất cao nhất.`;
    }
  }

  return {
    estimatedWattage: estimated,
    recommendedPsuWattage: recommendedPsu,
    selectedPsuWattage: selectedPsu,
    headroomWattage: headroom,
    status,
    statusMessage
  };
}

// 2. Hardware Tier Evaluation
function getCpuTier(cpu?: Product): number {
  if (!cpu) return 1;
  const name = (cpu.name || '').toLowerCase();
  if (name.includes('9800x3d') || name.includes('7800x3d') || name.includes('14900') || name.includes('13900')) return 5;
  if (name.includes('14700') || name.includes('13700') || name.includes('7700') || name.includes('9700') || name.includes('i7')) return 4;
  if (name.includes('14600') || name.includes('13600') || name.includes('7600x') || name.includes('7600') || name.includes('i5-13') || name.includes('i5-14')) return 3.5;
  if (name.includes('12400') || name.includes('5600') || name.includes('5500') || name.includes('i5-12')) return 2.8;
  if (name.includes('i3') || name.includes('3200') || name.includes('4100')) return 1.5;
  return 2.5;
}

function getGpuTier(vga?: Product): number {
  if (!vga) return 0;
  const name = (vga.name || '').toLowerCase();
  if (name.includes('4090') || name.includes('5090')) return 5.5;
  if (name.includes('4080') || name.includes('5080') || name.includes('7900 xtx')) return 4.8;
  if (name.includes('4070 ti') || name.includes('5070') || name.includes('7900 xt')) return 4.2;
  if (name.includes('4070') || name.includes('7800 xt')) return 3.6;
  if (name.includes('4060 ti') || name.includes('5060 ti') || name.includes('7700 xt')) return 3.0;
  if (name.includes('4060') || name.includes('5060') || name.includes('3060') || name.includes('7600')) return 2.3;
  if (name.includes('3050') || name.includes('1660') || name.includes('6600')) return 1.6;
  if (name.includes('1650') || name.includes('1050')) return 1.0;
  return 2.0;
}

// 3. Bottleneck Analysis Engine
export function calculateBottleneckAnalysis(parts: Record<string, Product>): BottleneckAnalysis {
  const cpu = parts['cpu'];
  const vga = parts['vga'];

  if (!vga) {
    return {
      bottleneckPct: 75,
      dominantType: 'no_gpu',
      title: 'Chưa gắn Card đồ họa rời (VGA)',
      summary: 'Máy đang chạy đồ họa tích hợp iGPU, chỉ phù hợp xem phim, lướt web và văn phòng nhẹ.',
      cpuScore: getCpuTier(cpu) * 20,
      gpuScore: 10,
      balanceScore: 25
    };
  }

  const cpuTier = getCpuTier(cpu);
  const gpuTier = getGpuTier(vga);

  const cpuScore = Math.min(100, Math.round(cpuTier * 18));
  const gpuScore = Math.min(100, Math.round(gpuTier * 18));

  const diff = cpuTier - gpuTier;

  if (Math.abs(diff) <= 0.6) {
    return {
      bottleneckPct: 4,
      dominantType: 'balanced',
      title: 'Cấu hình cân bằng hoàn hảo (< 5% nghẽn)',
      summary: `CPU (${cpu?.name}) và GPU (${vga.name}) phát huy 98% sức mạnh lẫn nhau. Không có linh kiện nào bị lãng phí.`,
      cpuScore,
      gpuScore,
      balanceScore: 96
    };
  }

  if (diff < -0.6) {
    const pct = Math.min(45, Math.round(Math.abs(diff) * 14));
    return {
      bottleneckPct: pct,
      dominantType: 'cpu_bound',
      title: `Nghẽn CPU khoảng ${pct}%`,
      summary: `Card đồ họa ${vga.name} rất mạnh nhưng CPU ${cpu?.name || ''} hơi yếu. Trong các game nặng CPU (CS2, Valorant, GTA V), bạn có thể nâng cấp CPU để FPS tăng thêm 15-25%.`,
      cpuScore,
      gpuScore,
      balanceScore: Math.max(50, 100 - pct)
    };
  }

  const pct = Math.min(40, Math.round(diff * 12));
  return {
    bottleneckPct: pct,
    dominantType: 'gpu_bound',
    title: `Nghẽn GPU khoảng ${pct}%`,
    summary: `CPU ${cpu?.name} rất khỏe nhưng VGA ${vga.name} chưa xứng tầm. Dàn máy này có thể kéo tốt các VGA cao cấp hơn mà không lo bị nghẽn.`,
    cpuScore,
    gpuScore,
    balanceScore: Math.max(55, 100 - pct)
  };
}

// 4. Realistic Gaming FPS Telemetry for 6 Top Games
export function calculateGamingTelemetry(
  parts: Record<string, Product>,
  resolution: '1080p' | '1440p' | '4k'
): GameTelemetry[] {
  const vga = parts['vga'];
  const cpu = parts['cpu'];

  const gpuTier = getGpuTier(vga);
  const cpuTier = getCpuTier(cpu);

  // Multiplier by resolution
  const resMultiplier = resolution === '1080p' ? 1.0 : resolution === '1440p' ? 0.68 : 0.42;

  // Games definition and base benchmarks
  const gamesBase = [
    {
      id: 'cs2',
      name: 'Counter-Strike 2',
      genre: 'Esports FPS (DX11)',
      baseFps: 120,
      cpuWeight: 0.6,
      gpuWeight: 0.4,
      settingsNote: resolution === '4k' ? 'High 4K' : 'Very High 1080p'
    },
    {
      id: 'wukong',
      name: 'Black Myth: Wukong',
      genre: 'Action RPG (Unreal Engine 5)',
      baseFps: 35,
      cpuWeight: 0.25,
      gpuWeight: 0.75,
      settingsNote: gpuTier >= 4 ? 'Cinematic + DLSS' : 'High Setting + Frame Gen'
    },
    {
      id: 'cyberpunk',
      name: 'Cyberpunk 2077',
      genre: 'Ray Tracing AAA',
      baseFps: 32,
      cpuWeight: 0.3,
      gpuWeight: 0.7,
      settingsNote: gpuTier >= 4 ? 'Ray Tracing Ultra' : 'Ultra Quality'
    },
    {
      id: 'valorant',
      name: 'Valorant',
      genre: 'Tactical Shooter',
      baseFps: 180,
      cpuWeight: 0.75,
      gpuWeight: 0.25,
      settingsNote: 'Max Settings 144Hz+'
    },
    {
      id: 'gta5',
      name: 'GTA V / FiveM',
      genre: 'Open World Action',
      baseFps: 70,
      cpuWeight: 0.45,
      gpuWeight: 0.55,
      settingsNote: 'Very High / 2K Textures'
    },
    {
      id: 'lol',
      name: 'Liên Minh Huyền Thoại',
      genre: 'MOBA Esports',
      baseFps: 160,
      cpuWeight: 0.65,
      gpuWeight: 0.35,
      settingsNote: 'Max Settings Cực Đại'
    }
  ];

  return gamesBase.map(game => {
    let rawFps = 0;
    if (gpuTier === 0) {
      // Integrated GPU
      rawFps = Math.round(game.baseFps * 0.25 * resMultiplier);
    } else {
      const perfIndex = (cpuTier * game.cpuWeight + gpuTier * game.gpuWeight) / 2.5;
      rawFps = Math.round(game.baseFps * perfIndex * 1.55 * resMultiplier);
    }

    rawFps = Math.max(12, rawFps);

    let experienceRating: GameTelemetry['experienceRating'] = 'laggy';
    let badgeText = 'Khó chơi';
    let progressPct = Math.min(100, Math.round((rawFps / 240) * 100));

    if (rawFps >= 200) {
      experienceRating = 'ultra';
      badgeText = '240Hz Pro';
    } else if (rawFps >= 120) {
      experienceRating = 'ultra';
      badgeText = '144Hz Siêu Mượt';
    } else if (rawFps >= 60) {
      experienceRating = 'smooth';
      badgeText = '60 FPS Chuẩn';
    } else if (rawFps >= 35) {
      experienceRating = 'playable';
      badgeText = 'Chơi Tốt';
    } else {
      experienceRating = 'laggy';
      badgeText = 'Giật Lag';
    }

    return {
      id: game.id,
      name: game.name,
      genre: game.genre,
      fps: rawFps,
      fpsText: `${rawFps} FPS`,
      progressPct,
      experienceRating,
      badgeText,
      settingsNote: game.settingsNote
    };
  });
}
