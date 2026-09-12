import { redirect } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const prerender = false;

export function load(): ReturnType<PageLoad> {
  throw redirect(307, '/dashboard');
}
