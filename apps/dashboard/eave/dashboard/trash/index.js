const { AsyncLocalStorage } = require("node:async_hooks");
const express = require("express");
const { setTimeout } = require("node:timers/promises");


const app = express();

// Create an instance of AsyncLocalStorage
const asyncLocalStorage = new AsyncLocalStorage();

// Middleware to set a context-local variable
function eaveGlobCtxMiddleware(req, res, next) {
  const eaveGlobCtx = req.query;
  asyncLocalStorage.enterWith(eaveGlobCtx); // TODO: experimental feature... but run() sucks and doesnt seem to do what we want
  next();
}

async function sleep(s) {
  return new Promise((resolve, reject) => {
    setTimeout(s).then(resolve);
  })
}

async function dbAction() {
  await sleep(3);
  const globalVar = asyncLocalStorage.getStore();
  console.log(`EAVE FIRING EVENT W/ CTX: ${JSON.stringify(globalVar)}`);
}


app.use(eaveGlobCtxMiddleware);

app.get("/test", async (req, res) => {
  await dbAction();
  res.send(`Got vis id ${req.query.vis_id}\n`);
});

app.listen(5000, () => {
  console.log("Server is running on port 5000");
});
