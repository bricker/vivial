import { OutingBudget } from "../graphql/generated/graphql";

export function getBudgetLabel(budget: OutingBudget): string {
  switch (budget) {
    case OutingBudget.Free: {
      return "";
    }
    case OutingBudget.Inexpensive: {
      return "$";
    }
    case OutingBudget.Moderate: {
      return "$$";
    }
    case OutingBudget.Expensive: {
      return "$$$";
    }
    case OutingBudget.VeryExpensive: {
      return "$$$$";
    }
    default: {
      return "";
    }
  }
}
