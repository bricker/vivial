import { GlobalEaveState } from "./types";
import { uuidv4 } from "./util/uuid";

export const eaveState: GlobalEaveState = {
  /**
   * A unique ID per page view.
   * This initially gets set every time the document loads, but it may be changed by the navigation tracking too (eg React navigation).
   */
  pageViewId: uuidv4(),
};
