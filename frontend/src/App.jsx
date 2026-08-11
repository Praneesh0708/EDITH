import { useEffect, useRef, useState } from "react";
import "./App.css";

function App() {
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const [interviewStarted, setInterviewStarted] = useState(false);
  const [error, setError] = useState("");
  const [backendStatus, setBackendStatus] = useState("Checking...");

  const [sessionId, setSessionId] = useState("");
  const [question, setQuestion] = useState("");
  const [questionNumber, setQuestionNumber] = useState(0);

  const [recording, setRecording] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [transcribedAnswer, setTranscribedAnswer] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/status")
      .then((response) => response.json())
      .then((data) => {
        setBackendStatus(
          data.backend === "online"
            ? "Backend Connected"
            : "Backend Offline"
        );
      })
      .catch(() => {
        setBackendStatus("Backend Offline");
      });
  }, []);
  const speakQuestion = (text) => {
    if (!text) return;

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);

    utterance.rate = 0.95;
    utterance.pitch = 1;
    utterance.volume = 1;

    window.speechSynthesis.speak(utterance);
  };

  const startInterview = async () => {
    try {
      setError("");

      // Start camera + microphone
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });

      videoRef.current.srcObject = stream;

      // Start interview session in backend
      const response = await fetch(
        "http://127.0.0.1:8000/interview/start",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to start interview");
      }

      const data = await response.json();

      if (data.status !== "success") {
        throw new Error(data.message || "Interview could not be started");
      }

      // Store interview information
      setSessionId(data.session_id);
      setQuestion(data.question);
      setQuestionNumber(data.question_number);

      setInterviewStarted(true);
      speakQuestion(data.question);
    } catch (err) {
      console.error(err);

      setError(
        err.message ||
          "Camera, microphone, or backend connection failed."
      );
    }
  };

  const startRecording = () => {
    try {
      const stream = videoRef.current?.srcObject;

      if (!stream) {
        setError("Camera and microphone are not active.");
        return;
      }

      audioChunksRef.current = [];

      // Get only the microphone track
      const audioStream = new MediaStream(
        stream.getAudioTracks()
      );

      let recorder;

      if (MediaRecorder.isTypeSupported("audio/webm;codecs=opus")) {
        recorder = new MediaRecorder(audioStream, {
          mimeType: "audio/webm;codecs=opus",
        });
      } else if (MediaRecorder.isTypeSupported("audio/webm")) {
        recorder = new MediaRecorder(audioStream, {
          mimeType: "audio/webm",
        });
      } else {
        recorder = new MediaRecorder(audioStream);
      }

      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        const audioBlob = new Blob(
          audioChunksRef.current,
          {
            type:recorder.mimeType,
          }
        );

        await sendVoiceAnswer(audioBlob);
      };

      recorder.start();

      setRecording(true);
      setError("");
    } catch (err) {
      console.error(err);
      setError("Unable to start voice recording.");
    }
  };

  const stopRecording = () => {
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !== "inactive"
    ) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  const sendVoiceAnswer = async (audioBlob) => {
    try {
      console.log("Audio blob:", audioBlob);
      console.log("Audio size:", audioBlob.size);
      console.log("Audio type:", audioBlob.type);
      setProcessing(true);
      setError("");

      const formData = new FormData();

      formData.append("session_id", sessionId);

      formData.append(
        "audio_file",
        audioBlob,
        "answer.webm"
      );

      const response = await fetch(
        "http://127.0.0.1:8000/interview/voice-answer",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error(
          `Voice answer failed: ${response.status}`
        );
      }

      const data = await response.json();

      if (data.status !== "success") {
        throw new Error(
          data.message || "Voice answer processing failed."
        );
      }

      setTranscribedAnswer(
        data.transcribed_answer || ""
      );

      // Update next question
     if (data.next_question) {
        const nextQuestion =
         data.next_question.question || "";

        setQuestion(nextQuestion);

        speakQuestion(nextQuestion);
      }
      setQuestionNumber(
        (previous) => previous + 1
      );

    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="app">

      <header className="header">
        <div>
          <h1>EDITH</h1>
          <p>AI Interview & Placement Coach</p>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          {interviewStarted
            ? "Interview Active"
            : backendStatus}
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
              <p>
                Choose the type of interview you want to practice.
              </p>

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
              className={
                interviewStarted
                  ? "camera-video"
                  : "hidden"
              }
            />

          </div>

          <div className="interview-panel">

            <h2>
              {interviewStarted
                ? "Interview in Progress"
                : "Ready for your interview?"}
            </h2>

            {interviewStarted && (
              <>
                <div className="question-box">
                  <p>
                    Question {questionNumber}
                  </p>

                  <h3>{question}</h3>
                </div>

                <div className="voice-controls">

                  {!recording && !processing && (
                    <button
                      className="start-button"
                      onClick={startRecording}
                    >
                      🎤 Start Answer
                    </button>
                  )}

                  {recording && (
                    <button
                      className="start-button"
                      onClick={stopRecording}
                    >
                      ⏹ Stop Recording
                    </button>
                  )}

                  {processing && (
                    <div className="recording-status">
                      🧠 EDITH is analyzing your answer...
                    </div>
                  )}

                </div>

                {transcribedAnswer && (
                  <div className="answer-box">
                    <h3>Your Answer</h3>
                    <p>{transcribedAnswer}</p>
                  </div>
                )}
              </>
            )}

            {!interviewStarted && (
              <>
                <p>
                  EDITH will analyze your answers, communication,
                  technical knowledge and identify areas for improvement.
                </p>

                <button
                  className="start-button"
                  onClick={startInterview}
                >
                  🎤 Start Interview
                </button>
              </>
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