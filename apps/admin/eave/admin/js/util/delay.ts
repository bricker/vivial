export function delay({ ms }: { ms: number }): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
