
export type DocumentInput = {
  title: string;
  content: string;
  parent?: DocumentInput;
}

export type EaveDocument = {
  title: string;
  content: string;
  parent?: EaveDocument;
}