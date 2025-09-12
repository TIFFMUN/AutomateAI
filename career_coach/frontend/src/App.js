import { useState } from "react";
import axios from "axios";

const questions = [
  "1. When working on a group project, what role do you naturally gravitate towards?\nA) The visionary\nB) The analyst\nC) The facilitator",
  "2. You're given a task with a tight deadline. Your first instinct is to:\nA) Experiment\nB) Plan\nC) Ask colleagues",
  "3. Which statement best describes your ideal measure of success?\nA) Innovation\nB) Efficiency\nC) Positive feedback",
  "4. How do you prefer to learn new things?\nA) Trial and error\nB) Manuals/training\nC) Shadowing an expert",
  "5. A teammate is stuck. You are more likely to:\nA) Brainstorm\nB) Work step-by-step\nC) Listen & support",
  "6. Which task energizes you most?\nA) Building new systems\nB) Troubleshooting issues\nC) Presenting work"
];

export default function App() {
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);

  const handleChange = (e, idx) => {
    setAnswers({...answers, [`q${idx+1}`]: e.target.value});
  };

  const handleSubmit = async () => {
    const res = await axios.post("http://localhost:8000/career-coach", { answers });
    setResult(res.data);
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Career Coach Quiz</h1>
      {questions.map((q, idx) => (
        <div key={idx}>
          <p>{q}</p>
          <input type="text" onChange={(e) => handleChange(e, idx)} />
        </div>
      ))}
      <button onClick={handleSubmit}>Submit</button>
      {result && (
        <div style={{ marginTop: 20 }}>
          <h2>Profile Summary</h2>
          <p>{result.profile_summary}</p>
          <h2>Suggestions</h2>
          <p>{result.suggestions}</p>
        </div>
      )}
    </div>
  );
}
