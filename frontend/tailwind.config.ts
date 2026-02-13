import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#101217',
        panel: '#151924',
        muted: '#8892a0',
        accent: '#93c5fd'
      }
    }
  },
  plugins: []
};

export default config;
