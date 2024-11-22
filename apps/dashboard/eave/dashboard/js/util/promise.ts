export function floatingPromise(func: (...args: unknown[]) => Promise<unknown>): (...args: unknown[]) => void {
  return (...args: unknown[]) => {
    void func(...args);
  };
}
