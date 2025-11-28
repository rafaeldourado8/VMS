// frontend/src/lib/utils.ts
/**
 * Utilitários para frontend
 * - cn: helper para concatenar classes CSS (compatível com cva)
 * - manipulação de tokens (sessionStorage)
 * - helpers de normalização de URLs retornadas pela API (webrtc/hls)
 * - parse simplificado de respostas paginadas
 */

/* -------------------------
   Helper de classes: cn()
   -------------------------
   Comportamento compatível com muitos libs:
   - aceita strings, arrays, objetos, falsy values
   - plana arrays aninhados
   - produz string com classes separadas por espaço
*/
type ClassValue = string | number | null | undefined | boolean | ClassDictionary | ClassArray;
interface ClassDictionary { [id: string]: any; }
interface ClassArray extends Array<ClassValue> {}

export function cn(...inputs: ClassValue[]): string {
  const classes: string[] = [];

  const handle = (val: ClassValue): void => {
    if (!val && val !== 0) return;

    if (typeof val === 'string' || typeof val === 'number') {
      classes.push(String(val));
      return;
    }

    if (Array.isArray(val)) {
      val.forEach(handle);
      return;
    }

    if (typeof val === 'object') {
      for (const key in val as ClassDictionary) {
        if ((val as ClassDictionary)[key]) {
          classes.push(key);
        }
      }
      return;
    }
  };

  inputs.forEach(handle);

  // simples merge; se precisar de conflito entre classes utilitárias (e.g. tailwind),
  // considere usar `tailwind-merge` (twMerge) junto com clsx.
  return classes.join(' ').trim();
}

/* -------------------------
   Token storage keys
   ------------------------- */
const ACCESS_KEY = 'access_token';
const REFRESH_KEY = 'refresh_token';

export const getAccessToken = (): string | null => {
  try { return sessionStorage.getItem(ACCESS_KEY); } catch { return null; }
};

export const getRefreshToken = (): string | null => {
  try { return sessionStorage.getItem(REFRESH_KEY); } catch { return null; }
};

export const setAccessToken = (token: string) => {
  try { sessionStorage.setItem(ACCESS_KEY, token); } catch {}
};

export const setRefreshToken = (token: string) => {
  try { sessionStorage.setItem(REFRESH_KEY, token); } catch {}
};

export const clearAuthTokens = () => {
  try {
    sessionStorage.removeItem(ACCESS_KEY);
    sessionStorage.removeItem(REFRESH_KEY);
  } catch {}
};

/* -------------------------
   Normalização de URLs / Thumbnails
   ------------------------- */
export const makeAbsoluteUrl = (url?: string | null): string => {
  if (!url) return '';
  try {
    if (url.startsWith('/')) {
      return `${window.location.origin}${url}`;
    }
    return url;
  } catch {
    return url || '';
  }
};

export const normalizeThumbnail = (thumb?: string | null): string | undefined => {
  if (!thumb) return undefined;
  return makeAbsoluteUrl(thumb);
};

/* -------------------------
   Normalizar câmera e responses
   ------------------------- */
export type RawCamera = any;
export type NormalizedCamera = {
  id: number;
  name: string;
  thumbnail_url?: string | null;
  webrtc_url?: string;
  hls_url?: string;
};

export const normalizeCamera = (c: RawCamera): NormalizedCamera => {
  const rawThumb = c.thumbnail_url ?? c.thumbnail ?? null;
  const thumb = normalizeThumbnail(rawThumb);
  const webrtcRaw = c.webrtc_url ?? c.webrtc ?? '';
  const hlsRaw = c.hls_url ?? c.hls ?? '';

  return {
    id: c.id,
    name: c.name,
    thumbnail_url: thumb ?? null,
    webrtc_url: webrtcRaw ? makeAbsoluteUrl(webrtcRaw) : '',
    hls_url: hlsRaw ? makeAbsoluteUrl(hlsRaw) : '',
  };
};

export const parseListResponse = <T = any>(payload: any): T[] => {
  if (!payload) return [];
  if (Array.isArray(payload)) return payload as T[];
  if (Array.isArray(payload.results)) return payload.results as T[];
  if (Array.isArray(payload.data)) return payload.data as T[];
  if (Array.isArray(payload.items)) return payload.items as T[];
  return [];
};