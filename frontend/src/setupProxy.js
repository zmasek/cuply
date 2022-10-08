const proxy = require("http-proxy-middleware");

module.exports = app => {
  app.use(proxy("/api", { target: process.env.REACT_APP_API_TARGET }));
  app.use(proxy("/microcontroller", { target: process.env.REACT_APP_WS_TARGET, ws: true }));
  app.use(proxy("/media", { target: process.env.REACT_APP_MEDIA_TARGET }));
};
