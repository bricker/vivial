class CacheEntry<T> {
  key: string;

  value: T;

  ttl: number | undefined;

  constructor(key: string, value: T, ttlMillis: number | null = null) {
    this.key = key;
    this.value = value;

    if (ttlMillis) {
      this.ttl = Date.now() + ttlMillis;
    }
  }
}

class Cache {
  private storage: {[key:string]: CacheEntry<unknown>} = {};

  async getOrSet<T>(key: string, ttlMillis: number | null, func: () => Promise<T>): Promise<T> {
    const cachedValue = <T | undefined> this.get(key);
    if (cachedValue) {
      return cachedValue;
    }

    const value = await func();
    this.set(key, value, ttlMillis);
    return value;
  }

  set<T>(key: string, value: T, ttlMillis: number | null = null) {
    const entry = new CacheEntry(key, value, ttlMillis);
    this.storage[key] = entry;
  }

  get<T>(key: string): T | undefined {
    const entry = this.storage[key];
    const now = Date.now();

    if (!entry) return undefined;
    if (entry && !entry.ttl) return <T>entry.value;
    if (entry && entry.ttl && entry.ttl > now) return <T>entry.value;

    if (entry && entry.ttl && entry.ttl <= now) {
      this.remove(key);
    }

    return undefined;
  }

  remove(key: string) {
    delete this.storage[key];
  }

  clear() {
    this.storage = {};
  }
}

export default new Cache();
