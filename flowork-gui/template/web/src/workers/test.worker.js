//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\src\workers\test.worker.js total lines 7 
//#######################################################################

self.onmessage = e => { console.log('Message received from main script:', e.data); self.postMessage('Hello from worker'); };
