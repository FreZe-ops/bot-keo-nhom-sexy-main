const path = require("path");
const pythonInterpreter = process.platform === "win32"
  ? (process.env.PYTHON_PATH || "python")
  : "./venv/bin/python";

/** PM2 Ecosystem - Chạy 4 Bot Python độc lập cho 4 Session (NS1, NS2, NS3, NS4) */
module.exports = {
  apps: [
    {
      name: "bot_NS1",
      script: "bot_multi_session.py",
      interpreter: pythonInterpreter,
      cwd: __dirname,
      instances: 1,
      autorestart: true,
      watch: false,
      max_restarts: 15,
      restart_delay: 8000,
      env: {
        PYTHONUNBUFFERED: "1",
        NAME_SERVICE: "NS1",
      },
    },
    {
      name: "bot_NS2",
      script: "bot_multi_session.py",
      interpreter: pythonInterpreter,
      cwd: __dirname,
      instances: 1,
      autorestart: true,
      watch: false,
      max_restarts: 15,
      restart_delay: 8000,
      env: {
        PYTHONUNBUFFERED: "1",
        NAME_SERVICE: "NS2",
      },
    },
    {
      name: "bot_NS3",
      script: "bot_multi_session.py",
      interpreter: pythonInterpreter,
      cwd: __dirname,
      instances: 1,
      autorestart: true,
      watch: false,
      max_restarts: 15,
      restart_delay: 8000,
      env: {
        PYTHONUNBUFFERED: "1",
        NAME_SERVICE: "NS3",
      },
    },
    {
      name: "bot_NS4",
      script: "bot_multi_session.py",
      interpreter: pythonInterpreter,
      cwd: __dirname,
      instances: 1,
      autorestart: true,
      watch: false,
      max_restarts: 15,
      restart_delay: 8000,
      env: {
        PYTHONUNBUFFERED: "1",
        NAME_SERVICE: "NS4",
      },
    },
  ],
};
