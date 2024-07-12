import axios from "axios";
import React, { useEffect, useState } from "react";
import styles from "./Quiz.module.css";
import { COOKIE_PREFIX, getCookie, setCookie } from "./cookies";
import { Question, Quiz } from "./types";

const STREAK_COOKIE_NAME = `${COOKIE_PREFIX}streak`;
const PASSING_SCORE = 7;

const getStreakFromCookie = (): number => {
  const streakCookie = getCookie(STREAK_COOKIE_NAME);
  if (streakCookie) {
    return parseInt(streakCookie, 10);
  } else {
    return 0;
  }
};

const QuizPage = () => {
  const qp = new URLSearchParams(window.location.search);
  const cheatMode = qp.has("cheatmode");

  // State to track selected answers and correctness
  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedAnswers, setSelectedAnswers] = useState<number[]>([]);
  const [streak, setStreak] = useState(getStreakFromCookie());
  const [score, setScore] = useState(0);

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
  const handleAnswerSelect = (question: Question, questionIndex: number, answerIndex: number) => {
    if (selectedAnswers[questionIndex] !== undefined) {
      // If an answer has already been selected, do nothing
      return;
    }

    // Clone the selectedAnswers array to modify it immutably
    const updatedAnswers = [...selectedAnswers];
    updatedAnswers[questionIndex] = answerIndex;

    setSelectedAnswers(updatedAnswers);

    if (question.correct_answer_index === answerIndex) {
      setScore((prevScore) => prevScore + 1);
    }

    if (quiz && updatedAnswers.length === quiz.questions.length) {
      if (score >= PASSING_SCORE) {
        setStreak((prevStreak) => {
          const newStreak = prevStreak + 1;
          setCookie({ name: STREAK_COOKIE_NAME, value: newStreak.toString(10) });
          return newStreak;
        });
      } else {
        setStreak(() => {
          const newStreak = 0;
          setCookie({ name: STREAK_COOKIE_NAME, value: newStreak.toString(10) });
          return newStreak;
        });
      }
    }
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
          onClick={() => handleAnswerSelect(question, questionIndex, index)}
        >
          {cheatMode && index === question.correct_answer_index ? ">" : ""} {choice}
        </div>
      );
    });
  };

  // Function to render all questions
  const renderQuestions = (): React.ReactElement[] | undefined => {
    return quiz?.questions.map((question: Question, index: number) => (
      <div key={index} className={styles.question}>
        <div className={styles.questionTitle}>
          {index + 1}. {question.text}
        </div>
        <div className={styles.choices}>{renderChoices(question, index)}</div>
      </div>
    ));
  };

  const renderResults = (): React.ReactElement | null => {
    if (!quiz || quiz.questions.length === 0 || selectedAnswers.length < quiz.questions.length) {
      return null;
    }

    const passed = score >= PASSING_SCORE;

    let resultsClass = "";
    if (passed) {
      resultsClass = "pass";
    } else {
      resultsClass = "fail";
    }

    return (
      <div className={`${styles.results} ${styles[resultsClass]}`}>
        <h2>
          Score: {score} / {quiz.questions.length}
        </h2>
        <span>{passed ? "You passed!" : "You failed!"}</span>
        <br />
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
          <span>Current streak: {streak}</span>
          <h1>{quiz?.title}</h1>
          <h4>Score {PASSING_SCORE} or better to pass!</h4>
          {renderQuestions()}
          {renderResults()}
        </>
      )}
    </div>
  );
};

export default QuizPage;
