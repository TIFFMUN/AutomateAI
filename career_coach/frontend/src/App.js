import { useState } from "react";
import axios from "axios";
import "./App.css"; // Make sure this imports your app.css

const questions = [
  {
    q: "1. When working on a group project, what role do you naturally gravitate towards?",
    options: ["A) The visionary", "B) The analyst", "C) The facilitator"],
  },
  {
    q: "2. You're given a task with a tight deadline. Your first instinct is to:",
    options: ["A) Experiment", "B) Plan", "C) Ask colleagues"],
  },
  {
    q: "3. Which statement best describes your ideal measure of success?",
    options: ["A) Innovation", "B) Efficiency", "C) Positive feedback"],
  },
  {
    q: "4. How do you prefer to learn new things?",
    options: ["A) Trial and error", "B) Manuals/training", "C) Shadowing an expert"],
  },
  {
    q: "5. A teammate is stuck. You are more likely to:",
    options: ["A) Brainstorm", "B) Work step-by-step", "C) Listen & support"],
  },
  {
    q: "6. Which task energizes you most?",
    options: ["A) Building new systems", "B) Troubleshooting issues", "C) Presenting work"],
  },
];

export default function App() {
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e, idx) => {
    setAnswers({ ...answers, [`q${idx + 1}`]: e.target.value });
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const res = await axios.post("http://localhost:8000/career-coach", { answers });
      console.log(res.data);
      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert("Error submitting quiz. Check console for details.");
    }
    setLoading(false);
  };

  return (
    <div className="container">
      <h1>Career Coach Quiz</h1>
      {questions.map((qObj, idx) => (
        <div key={idx} className="question-block">
          <p>{qObj.q}</p>
          {qObj.options.map((opt) => (
            <label key={opt} className="option-label">
              <input
                type="radio"
                name={`q${idx + 1}`}
                value={opt}
                checked={answers[`q${idx + 1}`] === opt}
                onChange={(e) => handleChange(e, idx)}
              />
              {opt}
            </label>
          ))}
        </div>
      ))}
      <button onClick={handleSubmit} disabled={loading}>
        {loading ? "Submitting..." : "Submit"}
      </button>
      {result && (
        <div className="result">
          <h2>Profile Summary</h2>
          <p>{result.profile_summary}</p>
          <h2>Suggestions</h2>
          <p>{result.suggestions}</p>
        </div>
      )}
    </div>
  );
}

