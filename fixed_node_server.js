const http = require('http');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');

const PORT = 80;
const STATIC_DIR = '/opt/AItestdemo/frontend/dist';
const BACKEND_URL = 'http://127.0.0.1:8080';

// MIME types
const mimeTypes = {
  '.html': 'text/html',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2'
};

function getContentType(filePath) {
  const ext = path.extname(filePath);
  return mimeTypes[ext] || 'text/plain';
}

function serveFile(res, filePath) {
  try {
    const content = fs.readFileSync(filePath);
    const contentType = getContentType(filePath);

    res.writeHead(200, {
      'Content-Type': contentType,
      'Content-Length': content.length,
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    });
    res.end(content);
    console.log(`[FILE] Served: ${filePath} (${content.length} bytes)`);
    return true;
  } catch (error) {
    console.error(`[ERROR] Failed to serve file: ${filePath}`, error);
    return false;
  }
}

function proxyRequest(req, res) {
  const backendUrl = `${BACKEND_URL}${req.url}`;
  console.log(`[PROXY] ${req.method} ${req.url} -> ${backendUrl}`);

  const options = {
    method: req.method,
    headers: {}
  };

  // Copy headers except host
  for (const [key, value] of Object.entries(req.headers)) {
    if (key.toLowerCase() !== 'host') {
      options.headers[key] = value;
    }
  }

  const proxyReq = http.request(backendUrl, options, (proxyRes) => {
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res);
    console.log(`[PROXY] Response: ${proxyRes.statusCode}`);
  });

  proxyReq.on('error', (err) => {
    console.error(`[PROXY] Error:`, err);
    if (!res.headersSent) {
      res.writeHead(502);
      res.end('Bad Gateway');
    }
  });

  req.pipe(proxyReq);
}

const server = http.createServer((req, res) => {
  const url = req.url;

  console.log(`[${new Date().toISOString()}] ${req.method} ${url}`);

  // API requests
  if (url.startsWith('/api/v1/') || url.startsWith('/docs') || url.startsWith('/health') || url.startsWith('/openapi.json')) {
    proxyRequest(req, res);
    return;
  }

  // Static files
  let filePath = path.join(STATIC_DIR, url === '/' ? 'index.html' : url);

  // Remove query string
  filePath = filePath.split('?')[0];

  console.log(`[STATIC] Request: ${url} -> ${filePath}`);

  // Check if file exists
  fs.access(filePath, fs.constants.F_OK, (err) => {
    if (err) {
      // SPA fallback - serve index.html for non-file requests
      if (!path.extname(url.split('/').pop())) {
        const indexPath = path.join(STATIC_DIR, 'index.html');
        fs.access(indexPath, fs.constants.F_OK, (indexErr) => {
          if (!indexErr) {
            console.log(`[SPA] Fallback: ${url} -> ${indexPath}`);
            if (!serveFile(res, indexPath)) {
              res.writeHead(500);
              res.end('Internal Server Error');
            }
            return;
          }
        });
        return;
      }

      // If we get here, it's a 404
      if (!res.headersSent) {
        res.writeHead(404);
        res.end('File Not Found');
        console.log(`[404] File not found: ${filePath}`);
      }
      return;
    }

    // Serve the file
    if (!serveFile(res, filePath)) {
      if (!res.headersSent) {
        res.writeHead(500);
        res.end('Internal Server Error');
      }
    }
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Fixed Node.js Server started!`);
  console.log(`📍 Server: http://47.101.190.42`);
  console.log(`📍 Local: http://localhost`);
  console.log(`🔧 API Proxy: /api/v1/* -> ${BACKEND_URL}`);
  console.log(`📁 Static Dir: ${STATIC_DIR}`);
  console.log(`⏰ Port: ${PORT}`);
  console.log('='.repeat(50));
  console.log('💡 Press Ctrl+C to stop');
  console.log('='.repeat(50));
});

server.on('error', (err) => {
  if (err.code === 'EADDRINUSE') {
    console.error(`❌ Port ${PORT} is already in use`);
  } else {
    throw err;
  }
});

process.on('SIGINT', () => {
  console.log('\n👋 Shutting down server...');
  server.close(() => {
    console.log('✅ Server stopped');
    process.exit(0);
  });
});