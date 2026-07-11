const { execSync } = require('child_process');
const path = require('path');

const root = path.resolve(__dirname, '..');

console.log('[dev] Building main + preload...');
try {
  execSync('npx tsc -p tsconfig.node.json', { cwd: root, stdio: 'inherit' });
} catch {
  console.error('[dev] TypeScript compilation failed');
  process.exit(1);
}

console.log('[dev] Building renderer...');
try {
  execSync('npx vite build', { cwd: root, stdio: 'inherit' });
} catch {
  console.error('[dev] Vite build failed');
  process.exit(1);
}

console.log('[dev] Starting Electron...');
try {
  execSync('npx electron .', { cwd: root, stdio: 'inherit' });
} catch {
  // Electron exits with code 0 on normal close
}
