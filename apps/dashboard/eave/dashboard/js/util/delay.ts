export function delay({ ms }: { ms: number }): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function floatingPromise(func: (...args: unknown[]) => Promise<unknown>): (...args: unknown[]) => void {
  return (...args: unknown[]) => {
    void func(...args);
  };
}
