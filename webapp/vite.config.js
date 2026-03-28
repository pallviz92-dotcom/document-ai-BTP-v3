import { defineConfig } from 'vite';

export default defineConfig({
build: {
rollupOptions: {
input: {
index: 'index.html',
login: 'login.html',
dashboard: 'dashboard.html',
zocrMatch: 'zocr-match.html'
}
}
}
});
