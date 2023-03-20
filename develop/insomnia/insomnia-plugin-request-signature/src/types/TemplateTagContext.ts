import { AppContext } from "./AppContext";
import { MetaContext } from './MetaContext';
import { RenderContext } from './RenderContext';
import { StoreContext } from './StoreContext';
import { NetworkContext } from './NetworkContext';
import { UtilContext } from './UtilContext';
import { RequestContext } from "./RequestContext";

export interface TemplateTagContext {
  app: AppContext;
  context: RenderContext;
  request: RequestContext;
  meta: MetaContext;
  network: NetworkContext;
  renderPurpose: any;
  store: StoreContext;
  util: UtilContext;
}