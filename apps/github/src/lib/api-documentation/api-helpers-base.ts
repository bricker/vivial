import { CoreAPIHelperMixin } from "./core-api.js"
import { GithubAPIHelperMixin } from "./github-api.js"

export function APIHelpersMixin<TBase extends GithubAPIHelperMixin>(Base: TBase) {
  return class extends Base {}
}
