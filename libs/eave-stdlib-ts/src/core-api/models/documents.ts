export type DocumentInput = {
  title: string;
  content: string;
  parent: DocumentInput | null;
}

export type EaveDocument = {
  title: string;
  content: string;
  parent: EaveDocument | null;
}

export type DocumentSearchResult = {
    title: string;
    url: string;
}
