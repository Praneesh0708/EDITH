import { useEffect, useRef, useState } from "react";
import "./App.css";

function App() {
  const videoRef = useRef(null);

  const [interviewStarted, setInterviewStarted] = useState(false);
  const [error, setError] = useState("");
  const [backendStatus, setBackendStatus] = useState("Checking...");
  useEffect(() => {
  fetch("http://127.0.0.1:8000/api/status")
    .then((response) => response.json())
    .then((data) => {
      setBackendStatus(
        data.backend === "online" ? "Backend Connected" : "Backend Offline"
      );
    })
    .catch(() => {
      setBackendStatus("Backend Offline");
    });
}, []);

  const startInterview = async () => {
    try {
      setError("");

      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });

      videoRef.current.srcObject = stream;
      setInterviewStarted(true);
    } catch (err) {
      console.error(err);
      setError(
        "Camera or microphone permission was denied. Please allow access and try again."
      );
    }
  };

  return (
    <div className="edith-app">

      <header className="header">
        <div>
          <h1>EDITH</h1>
          <p>AI Interview & Placement Coach</p>
        </div>

        <div className="status">
          <span className="status-dot"></span>
         {interviewStarted ? "Interview Active" : backendStatus}
        </div>
      </header>

      <main className="dashboard">

        <section className="welcome">
          <h2>
            {interviewStarted
              ? "Your Interview Has Started"
              : "Welcome to EDITH"}
          </h2>

          <p>
            {interviewStarted
              ? "EDITH is ready to analyze your interview."
              : "Your adaptive AI-powered interview preparation assistant."}
          </p>
        </section>

        {!interviewStarted && (
          <section className="cards">

            <div className="card">
              <h3>📄 Resume</h3>
              <p>
                Upload your resume to create a personalized interview.
              </p>
              <button>Upload Resume</button>
            </div>

            <div className="card">
              <h3>💼 Job Role</h3>
              <p>Select the role you want to prepare for.</p>

              <select>
                <option>Select Job Role</option>
                <option>Software Developer</option>
                <option>Python Developer</option>
                <option>Java Developer</option>
                <option>AI/ML Engineer</option>
                <option>Data Scientist</option>
              </select>
            </div>

            <div className="card">
              <h3>🎯 Interview Type</h3>
              <p>Choose the type of interview you want to practice.</p>

              <select>
                <option>Select Interview Type</option>
                <option>Technical</option>
                <option>HR</option>
                <option>Technical + HR</option>
                <option>AI/ML</option>
              </select>
            </div>

          </section>
        )}

        <section className="camera-section">

          <div className="camera-box">

            {!interviewStarted && (
              <>
                <div className="camera-icon">📷</div>
                <h3>Camera Preview</h3>
                <p>
                  Your camera will appear here during the interview.
                </p>
              </>
            )}

            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className={interviewStarted ? "camera-video" : "hidden"}
            />

          </div>

          <div className="interview-panel">

            <h2>
              {interviewStarted
                ? "Interview in Progress"
                : "Ready for your interview?"}
            </h2>

            <p>
              {interviewStarted
                ? "Camera and microphone are active. The AI interview engine will be connected next."
                : "EDITH will analyze your answers, communication, technical knowledge and identify areas for improvement."}
            </p>

            {!interviewStarted && (
              <button
                className="start-button"
                onClick={startInterview}
              >
                🎤 Start Interview
              </button>
            )}

            {interviewStarted && (
              <div className="recording-status">
                🔴 Interview Active
              </div>
            )}

            {error && (
              <p className="error-message">
                {error}
              </p>
            )}

          </div>

        </section>

      </main>

      <footer>
        <p>EDITH • Adaptive AI Interview System</p>
      </footer>

    </div>
  );
}

export default App;