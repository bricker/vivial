import axios from "axios";
import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import styles from "./Quiz.module.css";
import { COOKIE_PREFIX, getCookie, setCookie } from "./cookies";
import { Question, Quiz } from "./types";

const STREAK_COOKIE_NAME = `${COOKIE_PREFIX}streak`;

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
        <div className={styles.questionTitle}>{index + 1}. {question.text}</div>
        <div className={styles.choices}>{renderChoices(question, index)}</div>
      </div>
    ));
  };

  const renderResults = (): React.ReactElement | null => {
    if (!quiz || quiz.questions.length === 0 || selectedAnswers.length < quiz.questions.length) {
      return null;
    }

    const score = quiz?.questions.reduce((acc, question, i) => {
      if (selectedAnswers[i] === question.correct_answer_index) {
        return acc + 1;
      } else {
        return acc;
      }
    }, 0);

    const passed = score >= quiz.questions.length;

    let resultsClass = "";
    let streak = 0;

    if (passed) {
      resultsClass = "pass";
      const streakCookie = getCookie(STREAK_COOKIE_NAME);
      if (streakCookie) {
        streak = parseInt(streakCookie, 10);
      }
      streak += 1;
      setCookie({ name: STREAK_COOKIE_NAME, value: streak.toString(10) })
    } else {
      resultsClass = "fail";
      setCookie({ name: STREAK_COOKIE_NAME, value: "0" })
    }

    return (
      <div className={`${styles.results} ${styles[resultsClass]}`}>
        <h2>Score: {score} / {quiz.questions.length}</h2>
        <span>{passed ? "You passed!" : "You failed!"}</span>
        <br/>
        <span>Streak: {streak}</span>
        <br />
        <a href="/">Try another one!</a>
      </div>
    );
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
          {renderResults()}
        </>
      )}
    </div>
  );
};

export default QuizPage;
