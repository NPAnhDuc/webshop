import { Product } from '../types/index.js';

/**
 * Remove Vietnamese accents and tone marks for fuzzy matching
 */
export function removeVietnameseTones(str: string): string {
  if (!str) return '';
  let s = str;
  s = s.replace(/à|á|ạ|ả|ã|â|ầ|ấ|ậ|ẩ|ẫ|ă|ằ|ắ|ặ|ẳ|ẵ/g, 'a');
  s = s.replace(/è|é|ẹ|ẻ|ẽ|ê|ề|ế|ệ|ể|ễ/g, 'e');
  s = s.replace(/ì|í|ị|ỉ|ĩ/g, 'i');
  s = s.replace(/ò|ó|ọ|ỏ|õ|ô|ồ|ố|ộ|ổ|ỗ|ơ|ờ|ớ|ợ|ở|ỡ/g, 'o');
  s = s.replace(/ù|ú|ụ|ủ|ũ|ư|ừ|ứ|ự|ử|ữ/g, 'u');
  s = s.replace(/ỳ|ý|ỵ|ỷ|ỹ/g, 'y');
  s = s.replace(/đ/g, 'd');
  s = s.replace(/À|Á|Ạ|Ả|Ã|Â|Ầ|Ấ|Ậ|Ẩ|Ẫ|Ă|Ằ|Ắ|Ặ|Ẳ|Ẵ/g, 'a');
  s = s.replace(/È|É|Ẹ|Ẻ|Ẽ|Ê|Ề|Ế|Ệ|Ể|Ễ/g, 'e');
  s = s.replace(/Ì|Í|Ị|Ỉ|Ĩ/g, 'i');
  s = s.replace(/Ò|Ó|Ọ|Ỏ|Õ|Ô|Ồ|Ố|Ộ|Ổ|Ỗ|Ơ|Ờ|Ớ|Ợ|Ở|Ỡ/g, 'o');
  s = s.replace(/Ù|Ú|Ụ|Ủ|Ũ|Ư|Ừ|Ứ|Ự|Ử|Ữ/g, 'u');
  s = s.replace(/Ỳ|Ý|Ỵ|Ỷ|Ỹ/g, 'y');
  s = s.replace(/Đ/g, 'd');
  // Combining diacritical marks
  s = s.replace(/[\u0300-\u036f]/g, '');
  return s.toLowerCase().trim();
}

/**
 * Normalizes multi-word Vietnamese search phrases into standard tech terms
 */
function normalizeSearchPhrases(text: string): string {
  let s = text;
  s = s.replace(/\b(card\s+man\s+hinh|card\s+do\s+hoa)\b/g, 'vga');
  s = s.replace(/\b(vi\s+xu\s+ly|chip\s+xu\s+ly)\b/g, 'cpu');
  s = s.replace(/\b(o\s+cung|o\s+dia)\b/g, 'ssd');
  s = s.replace(/\b(bo\s+nho\s+trong|thanh\s+ram)\b/g, 'ram');
  s = s.replace(/\b(bo\s+nguon|nguon\s+may\s+tinh)\b/g, 'psu');
  s = s.replace(/\b(man\s+hinh|hien\s+thi)\b/g, 'screen');
  s = s.replace(/\b(may\s+tinh\s+xach\s+tay|may\s+xach\s+tay)\b/g, 'laptop');
  s = s.replace(/\b(may\s+tinh\s+de\s+ban|may\s+de\s+ban|thung\s+may)\b/g, 'pc');
  s = s.replace(/\b(may\s+tinh)\b/g, 'laptop');
  return s;
}

/**
 * Simple Levenshtein distance for typo tolerance (e.g. asuss -> asus)
 */
function isCloseMatch(a: string, b: string): boolean {
  if (a === b) return true;
  if (Math.abs(a.length - b.length) > 1) return false;

  let diff = 0;
  let i = 0, j = 0;
  while (i < a.length && j < b.length) {
    if (a[i] !== b[j]) {
      diff++;
      if (diff > 1) return false;
      if (a.length > b.length) i++;
      else if (b.length > a.length) j++;
      else { i++; j++; }
    } else {
      i++; j++;
    }
  }
  return true;
}

export interface SearchMatch {
  product: Product;
  score: number;
}

/**
 * Intelligent Smart Search Engine:
 * - Multi-token matching (All keywords must be satisfied)
 * - Accent-insensitive (Tiếng Việt có dấu / không dấu)
 * - Hardware compound phrase normalization (Card màn hình -> VGA, Ổ cứng -> SSD)
 * - Typo tolerance for brand & product names (e.g. asuss -> asus)
 * - Relevance scoring & ranking
 */
export function searchProducts(products: Product[], query: string): Product[] {
  if (!query || !query.trim()) return products;

  const rawQuery = query.toLowerCase().trim();
  const normalizedQuery = removeVietnameseTones(rawQuery);
  const phraseNormalized = normalizeSearchPhrases(normalizedQuery);

  const tokens = phraseNormalized.split(/\s+/).filter(t => t.length > 0);
  if (tokens.length === 0) return products;

  const matches: SearchMatch[] = [];

  for (const product of products) {
    const normName = removeVietnameseTones(product.name);
    const normBrand = removeVietnameseTones(product.brandName);
    const normCategory = removeVietnameseTones(product.categorySlug);
    const normDesc = removeVietnameseTones(product.description || '');

    const normCpu = product.specs.cpu_model ? removeVietnameseTones(product.specs.cpu_model) : '';
    const normGpu = product.specs.gpu_model ? removeVietnameseTones(product.specs.gpu_model) : '';
    const normPanel = product.specs.panel ? removeVietnameseTones(product.specs.panel) : '';
    const normScreen = product.specs.screen_inch ? `${product.specs.screen_inch} inch` : '';

    const combinedSearchText = `${normName} ${normBrand} ${normCategory} ${normCpu} ${normGpu} ${normPanel} ${normScreen} ${normDesc}`;

    let allTokensMatched = true;
    let score = 0;

    for (const token of tokens) {
      // 1. Direct substring in product information
      if (combinedSearchText.includes(token)) {
        if (normName.includes(token)) score += 35;
        else if (normBrand.includes(token)) score += 25;
        else if (normGpu.includes(token) || normCpu.includes(token)) score += 20;
        else score += 10;
        continue;
      }

      // 2. Screen synonym fallback (if token is 'screen', check if product has panel or screen_inch)
      if (token === 'screen' && (product.specs.panel || product.specs.screen_inch || normCategory === 'monitor')) {
        score += 20;
        continue;
      }

      // 3. Typo tolerance for brand (e.g. asuss -> asus, samsng -> samsung)
      if (token.length >= 4 && isCloseMatch(token, normBrand)) {
        score += 20;
        continue;
      }

      // Token not matched
      allTokensMatched = false;
      break;
    }

    if (allTokensMatched) {
      // Exact sequence match bonus
      if (normName.includes(normalizedQuery)) score += 60;
      if (product.isHot) score += 5;

      matches.push({ product, score });
    }
  }

  // Sort by highest score first
  matches.sort((a, b) => b.score - a.score);

  return matches.map(m => m.product);
}
