/// <reference types="@sveltejs/kit" />

declare namespace App {
  interface Locals {}
  interface PageData {}
  interface Error {}
  interface Platform {}
}

declare module '*.svelte' {
  import type { ComponentType } from 'svelte';
  const component: ComponentType;
  export default component;
}
