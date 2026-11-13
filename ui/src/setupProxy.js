// Used only by `npm start`. Forwards /api requests to API_PROXY_TARGET so the
// browser talks to localhost and the API needs no CORS entry for it.
const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function (app) {
  const target = process.env.API_PROXY_TARGET;
  if (!target) return;

  app.use(
    '/api',
    createProxyMiddleware({
      target,
      changeOrigin: true,
      pathRewrite: { '^/api': '' },
    })
  );
};
