export type Question = {
  text: string;
  choices: string[];
  correct_answer_index: number;
}

export type Quiz = {
  title: string;
  questions: Question[];
}
