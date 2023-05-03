export interface ApiClientBase {
  getFileContent(url: string): Promise<string | null>
}