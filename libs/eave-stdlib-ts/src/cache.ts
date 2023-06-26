import { createClient } from 'redis';
import { RedisCommandArgument } from '@redis/client/dist/lib/commands/index.js';
import { SetOptions } from '@redis/client/dist/lib/commands/SET.js';
import { google } from '@google-cloud/redis/build/protos/protos.js';
import { sharedConfig } from './config.js';
import eaveLogger from './logging.js';
import { redact } from './util.js';

export interface Cache {
  get: (key: RedisCommandArgument) => Promise<RedisCommandArgument | null>;
  set: (key: RedisCommandArgument, value: RedisCommandArgument | number, options?: SetOptions) => Promise<RedisCommandArgument | null>;
  del: (keys: RedisCommandArgument | RedisCommandArgument[]) => Promise<number>;
  ping: () => Promise<string>;
  quit: () => Promise<string>;
}

class CacheEntry {
  key: string;

  value: string;

  ex?: number;

  ts: number;

  constructor(key: string, value: string, ex?: number) {
    this.key = key;
    this.value = value;
    this.ex = ex;
    this.ts = new Date().getTime();
  }

  get expired(): boolean {
    if (this.ex === undefined) {
      return false;
    }

    const now = new Date().getTime();
    return this.ts + this.ex < now;
  }
}

export class EphemeralCache implements Cache {
  private storage: {[key:string]: CacheEntry} = {};

  async get(key: RedisCommandArgument): Promise<RedisCommandArgument | null> {
    const entry = this.storage[key.toString()];
    if (entry === undefined) {
      return null;
    }

    if (entry.expired) {
      // TODO: Not threadsafe
      await this.del(key);
      return null;
    }

    return entry.value;
  }

  async set(key: RedisCommandArgument, value: RedisCommandArgument | number, options?: SetOptions): Promise<RedisCommandArgument | null> {
    const entry = new CacheEntry(key.toString(), value.toString(), options?.EX);
    this.storage[key.toString()] = entry;
    return '1';
  }

  async del(keys: RedisCommandArgument | Array<RedisCommandArgument>): Promise<number> {
    let k: RedisCommandArgument[];

    if (keys.length === 0) {
      return 0;
    }
    if (keys instanceof Array) {
      k = keys;
    } else {
      k = [keys];
    }

    let count = 0;
    for (const key of k) {
      if (this.storage[key.toString()] !== undefined) {
        delete this.storage[key.toString()];
        count += 1;
      }
    }

    return count;
  }

  async ping(): Promise<string> {
    return '1';
  }

  async quit(): Promise<string> {
    return '1';
  }
}

async function loadCacheImpl(): Promise<Cache> {
  const redisInstance = await sharedConfig.redisInstance();
  if (!redisInstance) {
    const impl = new EphemeralCache();
    return impl;
  }

  const redisAuth = await sharedConfig.redisAuth();
  const redisDb = await sharedConfig.redisCacheDb();
  eaveLogger.debug(`Redis connection: host=${redisInstance.host}, port=${redisInstance.port}, db=${redisDb}, auth=${redact(redisAuth)}...`);

  const impl = createClient({
    socket: {
      host: redisInstance.host || undefined,
      port: redisInstance.port || undefined,
      tls: redisInstance.transitEncryptionMode === google.cloud.redis.v1.Instance.TransitEncryptionMode.SERVER_AUTHENTICATION,
      ca: redisInstance.serverCaCerts ? redisInstance.serverCaCerts[0]?.cert || undefined : undefined,
    },
    database: parseInt(redisDb, 10),
    password: redisAuth,
    pingInterval: 1000 * 60 * 5,
  });

  impl.on('error', (e) => { eaveLogger.error(e); });
  impl.on('connect', () => { eaveLogger.debug('redis client connected'); });
  impl.on('reconnecting', () => { eaveLogger.debug('redis client reconnecting'); });
  impl.on('ready', () => { eaveLogger.debug('redis client ready'); });

  await impl.connect();
  return impl;
}

let _PROCESS_CACHE_CLIENT: Cache | undefined;

export default async function client(): Promise<Cache> {
  if (_PROCESS_CACHE_CLIENT === undefined) {
    _PROCESS_CACHE_CLIENT = await loadCacheImpl();
  }
  return _PROCESS_CACHE_CLIENT;
}

export function cacheInitialized(): boolean {
  return _PROCESS_CACHE_CLIENT !== undefined;
}
