import '../app.css';
import type { LayoutData } from './$types';

export const prerender = false;
export const ssr = false;

export function load(): LayoutData {
  return {};
}
