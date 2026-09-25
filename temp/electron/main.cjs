const { app, BrowserWindow, shell } = require('electron')
const path = require('node:path')
const { spawn } = require('node:child_process')

const port = Number(process.env.ZS_DUMPER_UI_PORT || 3010)
let nextProcess

function startNext() {
  const nextBin = path.join(__dirname, '..', 'node_modules', 'next', 'dist', 'bin', 'next')
  nextProcess = spawn(process.execPath, [nextBin, 'start', '-p', String(port)], {
    cwd: path.join(__dirname, '..'),
    env: { ...process.env, NODE_ENV: 'production' },
    stdio: 'ignore',
    windowsHide: true,
  })
}

async function createWindow() {
  const window = new BrowserWindow({
    width: 1440,
    height: 920,
    minWidth: 1060,
    minHeight: 700,
    backgroundColor: '#09090b',
    autoHideMenuBar: true,
    title: 'ZS-DUMPER',
    webPreferences: { contextIsolation: true, nodeIntegration: false },
  })
  await window.loadURL(`http://127.0.0.1:${port}`)
  window.webContents.setWindowOpenHandler(({ url }) => { shell.openExternal(url); return { action: 'deny' } })
}

app.whenReady().then(async () => { startNext(); await new Promise((resolve) => setTimeout(resolve, 1200)); await createWindow() })
app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit() })
app.on('before-quit', () => { if (nextProcess) nextProcess.kill() })
app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow() })
