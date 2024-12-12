import { OutingBudget } from "../graphql/generated/graphql";

export function getBudgetLabel(budget: OutingBudget): string {
  if (budget === OutingBudget.Inexpensive) {
    return "$";
  }
  if (budget === OutingBudget.Moderate) {
    return "$$";
  }
  if (budget === OutingBudget.Expensive) {
    return "$$$";
  }
  if (budget === OutingBudget.VeryExpensive) {
    return "$$$$";
  }
  return ""; // Free.
}
