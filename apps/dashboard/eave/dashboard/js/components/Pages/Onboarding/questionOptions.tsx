import { useState } from "react";

interface Question {
  // NOTE: key values are read by backend and need to be kept in sync
  key: string;
  text: string;
  options: QuestionOption[];
}

export interface QuestionOption {
  readonly value: string;
  readonly label: string;
  readonly isFixed?: boolean;
  readonly isDisabled?: boolean;
}

const questions: Question[] = [
  {
    key: "platform",
    text: "Which platforms does your product support?",
    options: [
      { value: "web_app", label: "Web App" },
      { value: "ios", label: "iOS+" },
      { value: "android", label: "Android+" },
      { value: "native_desktop_app", label: "Native Desktop App" },
      { value: "wear_os", label: "Wear OS" },
      { value: "api_service", label: "API Service" },
    ],
  },
  {
    key: "languages",
    text: "Which programming languages are used to build your product?",
    options: [
      { value: "python", label: "Python" },
      { value: "ruby", label: "Ruby" },
      { value: "java", label: "Java" },
      { value: "swift", label: "Swift" },
      { value: "javascript", label: "JavaScript" },
      { value: "typescript", label: "TypeScript" },
      { value: "go", label: "Go" },
      { value: "kotlin", label: "Kotlin" },
      { value: "c++", label: "C++" },
    ],
  },
  {
    key: "frameworks",
    text: "Which libraries and frameworks are used to build your product?",
    options: [
      { value: "flask", label: "Flask" },
      { value: "express", label: "Express.js" },
      { value: "gin", label: "Gin" },
      { value: "fast_api", label: "FastAPI" },
      { value: "django", label: "Django" },
      { value: "ror", label: "Ruby on Rails" },
      { value: "nextjs", label: "Next.js" },
    ],
  },
  {
    key: "databases",
    text: "Which databases are used to store your product data?",
    options: [
      { value: "mysql", label: "MySQL" },
      { value: "postgresql", label: "PostgreSQL" },
      { value: "spanner", label: "Spanner" },
      { value: "mongodb", label: "MongoDB" },
    ],
  },
  {
    key: "third_party",
    text: "Which third party services are integrated into your product?",
    options: [
      { value: "openai", label: "OpenAI" },
      { value: "anthropic", label: "Anthropic" },
      { value: "gemini", label: "Gemini" },
      { value: "stripe", label: "Stripe" },
      { value: "paypal", label: "PayPal" },
      { value: "plaid", label: "Plaid" },
      { value: "square", label: "Square" },
    ],
  },
];

export const useQuestions = () => {
  return questions.map((question) => {
    const [value, setValue] = useState<readonly QuestionOption[]>([]);
    const [error, setError] = useState(false);
    return {
      key: question.key,
      question: question.text,
      options: question.options,
      value,
      setValue,
      error,
      setError,
    };
  });
};

export const copyString = `Getting started with Eave. Please answer the questions below. 
All information is kept confidential and strictly for the purposes of providing you with a proper product intelligence solution. 
${questions
  .map((question) => {
    return `${question.text} (E.g.  ${question.options
      .slice(0, 3)
      .map((opt) => opt.label)
      .join(", ")})`;
  })
  .join("\n")}`;
