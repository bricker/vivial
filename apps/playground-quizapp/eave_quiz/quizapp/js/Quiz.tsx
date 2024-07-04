import axios from "axios";
import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import styles from "./Quiz.module.css";
import { COOKIE_PREFIX, getCookie } from "./cookies";
import { Question, Quiz } from "./types";

const QuizPage = () => {
  // State to track selected answers and correctness
  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedAnswers, setSelectedAnswers] = useState<number[]>([]);

  const fetchQuiz = () => {
    setLoading(true);
    axios
      .get<Quiz>("/api/quiz")
      .then((response) => {
        setQuiz(response.data);
      })
      .catch((error) => {
        console.error(error);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  // Function to handle selecting an answer
  const handleAnswerSelect = (questionIndex: number, answerIndex: number) => {
    if (selectedAnswers[questionIndex] !== undefined) {
      // If an answer has already been selected, do nothing
      return;
    }

    // Clone the selectedAnswers array to modify it immutably
    const updatedAnswers = [...selectedAnswers];
    updatedAnswers[questionIndex] = answerIndex;

    setSelectedAnswers(updatedAnswers);
  };

  // Function to render choices for a question
  const renderChoices = (question: Question, questionIndex: number): React.ReactElement[] => {
    return question.choices.map((choice, index) => {
      const isCorrect = index === question.correct_answer_index;
      const isSelected = selectedAnswers[questionIndex] === index;

      // Determine the class based on correctness and selection
      let choiceClass = "";

      if (isSelected) {
        choiceClass = isCorrect ? "correct" : "wrong";
      } else if (selectedAnswers[questionIndex] !== undefined && isCorrect) {
        choiceClass = "correct";
      }

      return (
        <div
          key={index}
          className={`${styles.choice} ${styles[choiceClass]}`}
          onClick={() => handleAnswerSelect(questionIndex, index)}
        >
          {choice}
        </div>
      );
    });
  };

  // Function to render all questions
  const renderQuestions = (): React.ReactElement[] | undefined => {
    return quiz?.questions.map((question: Question, index: number) => (
      <div key={index} className={styles.question}>
        <div className={styles.questionTitle}>{question.text}</div>
        <div className={styles.choices}>{renderChoices(question, index)}</div>
      </div>
    ));
  };

  useEffect(() => {
    fetchQuiz();
  }, []);

  return (
    <div className={styles.quiz}>
      {loading ? (
        <div className={styles.loadingContainer}>
          <div className={styles.loader}></div>
        </div>
      ) : (
        <>
          <h1>{quiz?.title}</h1>
          {renderQuestions()}
        </>
      )}
    </div>
  );
};

export default QuizPage;
