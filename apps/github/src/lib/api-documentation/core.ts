import { ExpressAPIDocumentorBase } from "./base.js"
import { DocumentBuilderClassFactory, DocumentBuilderFactory } from "./builder.js";
import { CoreAPIHelperMixin } from "./core-api.js"
import { GithubAPIHelperMixin } from "./github-api.js"

const composedClass = DocumentBuilderMixin(CoreAPIHelperMixin(GithubAPIHelperMixin(ExpressAPIDocumentorBase)));
const DocumentBuilderMixin = DocumentBuilderFactory();

export function ExpressAPIDocumentorClassFactory<TBase extends DocumentBuilderMixin>(Base: TBase) {
  return class _ExpressAPIDocumentor {
  }
}

const DocumentBuilderClass = DocumentBuilderClassFactory(GithubAPIHelperMixin);
export const ExpressAPIDocumentorClass = ExpressAPIDocumentorClassFactory(DocumentBuilderClass);